import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

CASE_IDS = tuple("B%02d" % i for i in range(1, 11))
CLOUD_IDS = ("B01", "B04", "B06", "B08", "B10")


class ExtractionError(ValueError):
    pass


def extract_python(text):
    """Accept exactly one fenced block, labeled python, and no other fences."""
    if not isinstance(text, str):
        raise ExtractionError("response must be text")
    lines = text.splitlines(keepends=True)
    fences = [i for i, line in enumerate(lines) if re.match(r"^\s*(`{3,}|~{3,})", line)]
    if len(fences) != 2:
        raise ExtractionError("expected exactly one fenced python block")
    start, end = fences
    if lines[start].strip() != "```python" or lines[end].strip() != "```":
        raise ExtractionError("use exact ```python and ``` fences")
    if "".join(lines[:start]).strip() or "".join(lines[end + 1:]).strip():
        raise ExtractionError("no explanation outside the python block")
    code = "".join(lines[start + 1:end])
    if not code.strip():
        raise ExtractionError("empty python block")
    return code if code.endswith("\n") else code + "\n"


def case_path(root, case_id):
    if case_id not in CASE_IDS:
        raise ValueError("unknown case: " + case_id)
    directory = Path(root) / case_id
    if not directory.is_dir():
        raise ValueError("case directory missing: " + str(directory))
    return directory


def build_prompt(root, case_id):
    directory = case_path(root, case_id)
    # Deliberately never read reference.py or test_hidden.py here.
    sections = [(name, (directory / name).read_text(encoding="utf-8"))
                for name in ("prompt.md", "starter.py", "test_public.py")]
    return ("Solve this Python programming task. Return exactly one fenced code block "
            "labeled python, containing the complete replacement solution.py. "
            "Do not return tests, patches, or multiple code blocks.\n\n" +
            "\n\n".join("=== %s ===\n%s" % item for item in sections))


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    fd, tmp = tempfile.mkstemp(prefix="." + path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def append_jsonl(path, value):
    with Path(path).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def positive_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0)


def metrics(response, elapsed_seconds=None, ps=None, model=None):
    count, duration = response.get("eval_count"), response.get("eval_duration")
    speed = count / (duration / 1e9) if positive_number(count) and positive_number(duration) else None
    load = response.get("load_duration")
    total = response.get("total_duration")
    matching = []
    if isinstance(ps, dict):
        matching = [m for m in ps.get("models", []) if isinstance(m, dict)
                    and model in (m.get("name"), m.get("model"))] if model else []
    vram = matching[0].get("size_vram") if matching else None
    return {"tokens_per_second": speed,
            "tokens_per_second_unavailable_reason": None if speed is not None else "missing or non-positive eval_count/eval_duration",
            "vram_unavailable_reason": None if vram is not None else "matching model size_vram not available",
            "eval_count": count,
            "eval_duration_ns": duration, "elapsed_seconds": elapsed_seconds,
            "load_duration_seconds": load / 1e9 if positive_number(load) else (0 if load == 0 else None),
            "total_duration_seconds": total / 1e9 if positive_number(total) else None,
            "vram_mib": vram / (1024 ** 2) if positive_number(vram) else (0 if vram == 0 else None)}


def summarize(records, models, ids=CASE_IDS, repeats=2):
    result = {}
    for model in models:
        rows = [r for r in records if r.get("model") == model and r.get("phase") == "attempt"]
        unique = {}
        for row in rows:
            key = (row.get("case"), row.get("repeat"))
            if key[0] not in ids or key[1] not in range(1, repeats + 1):
                raise ValueError("unexpected case/repeat in results")
            if key in unique:
                raise ValueError("duplicate attempt: %r" % (key,))
            unique[key] = row
        statuses = {}
        for row in rows:
            status = row.get("status", "invalid")
            statuses[status] = statuses.get(status, 0) + 1
        solved = sum(r.get("status") == "solved" for r in rows)
        both = sum(all(unique.get((case, repeat), {}).get("status") == "solved"
                       for repeat in range(1, repeats + 1)) for case in ids)
        speeds = [r.get("metrics", {}).get("tokens_per_second") for r in rows]
        speeds = [v for v in speeds if positive_number(v)]
        elapsed = [r.get("metrics", {}).get("elapsed_seconds") for r in rows]
        elapsed = [v for v in elapsed if positive_number(v)]
        result[model] = {"planned": len(ids) * repeats, "completed": len(rows), "n": len(rows),
                         "solved": solved, "solved_denominator": len(ids) * repeats,
                         "all_repeats_solved_cases": both, "case_denominator": len(ids),
                         "call_failures": sum(v for k, v in statuses.items() if k.startswith("call_")),
                         "statuses": statuses, "speed_n": len(speeds),
                         "mean_tokens_per_second": sum(speeds) / len(speeds) if speeds else None,
                         "total_call_elapsed_seconds": sum(elapsed) if elapsed else None}
        item = result[model]
        call_success_statuses = {"solved", "test_failure", "extraction_failure", "timeout", "evaluator_error"}
        successes = [r for r in rows if r.get("status") in call_success_statuses]
        item["call_successes"] = len(successes)
        item["call_attempts"] = len(rows)
        item["not_run"] = len(ids) * repeats - len(rows)
        item["successful_response_quality_denominator"] = len(successes)
        item["mean_metrics"] = {}
        for field in ("elapsed_seconds", "load_duration_seconds", "tokens_per_second", "vram_mib"):
            values = [r.get("metrics", {}).get(field) for r in successes]
            values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)
                      and math.isfinite(v) and v >= 0]
            item["mean_metrics"][field] = {"mean": sum(values) / len(values) if values else None, "n": len(values)}
        item["per_case"] = {case: [unique.get((case, repeat), {}).get("status", "not_run")
                                  for repeat in range(1, repeats + 1)] for case in ids}
    return result
