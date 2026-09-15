"""Regenerable, read-only result interpretation; never imports submitted solutions.

Manifest v1 uses the core models/cases/repeats plan. Optional provenance keys:
participant, created_utc, source_commit, source_dirty, device_label, environment,
model_sources={tag: {model_card_url, license_url}}, options, evaluator backend/version/runner_hash metadata.
summary.json preserves core.summarize's model-keyed schema, adding completeness.
"""
import html
import json
import math
import os
from pathlib import Path
import platform
import subprocess

from .core import CASE_IDS, atomic_write, summarize, write_json

CALL_ERRORS = {"call_http_error", "call_transport_error", "call_invalid_json", "call_api_error", "call_incomplete_response"}
INFRA = CALL_ERRORS | {"evaluator_error"}
STATUSES = INFRA | {"solved", "test_failure", "extraction_failure", "timeout", "missing_response", "invalid_response_encoding"}
METRICS = ("elapsed_seconds", "load_duration_seconds", "tokens_per_second", "vram_mib")


def _command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=3, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def capture_environment():
    """No hostname, username, paths, environment variables or GPU serials."""
    system = platform.system()
    ram = None
    try:
        if system == "Darwin":
            value = _command(["sysctl", "-n", "hw.memsize"])
            ram = int(value) if value else None
        elif system == "Linux":
            ram = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        elif system == "Windows":
            value = _command(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                              "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"])
            ram = int(value) if value else None
    except (ValueError, OSError, TypeError):
        pass
    if not isinstance(ram, int) or ram <= 0:
        ram = None
    gpu = None
    raw = _command(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"])
    if raw:
        try:
            gpu = []
            for line in raw.splitlines():
                name, memory, driver = [part.strip() for part in line.split(",")]
                memory = float(memory)
                if not math.isfinite(memory) or memory < 0:
                    raise ValueError("invalid GPU memory")
                gpu.append({"name": name, "memory_total_mib": memory, "driver_version": driver})
        except (ValueError, TypeError):
            gpu = None
    logical_count = os.cpu_count()
    return {"os": {"system": system, "release": platform.release(), "machine": platform.machine()},
            "python_version": platform.python_version(),
            "cpu": {"architecture": platform.machine(), "logical_count": logical_count,
                    "logical_count_unavailable_reason": None if logical_count is not None else "logical CPU count unavailable",
                    "name": None, "name_unavailable_reason": "generic architecture only; identity intentionally omitted"},
            "ram_bytes": ram, "ram_unavailable_reason": None if ram else "safe RAM detection unavailable",
            "nvidia_gpus": gpu, "nvidia_unavailable_reason": None if gpu else "nvidia-smi unavailable, failed or invalid"}


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _json(text):
    def invalid(_):
        raise ValueError("non-finite JSON value")
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid)


def _read(path):
    if path.is_symlink():
        raise ValueError("symlink input rejected")
    return _json(path.read_text(encoding="utf-8"))


def _esc(value):
    if value is None:
        return "미기록"
    # Entity-encode all Markdown control characters, HTML and control whitespace.
    text = "".join("&#%d;" % ord(char) if char in "\\`*_{}[]()#+-.!|"
                   else html.escape(char, quote=True) for char in str(value))
    return " ".join(text.split())


def _link(root, relative, label):
    # Only caller-generated canonical relative names reach this function.
    target = root / relative
    if target.is_symlink() or not target.is_file():
        return ""
    if not target.resolve().is_relative_to(root.resolve()):
        return ""
    return "[%s](%s)" % (label, relative)


def _stem(manifest, model_index, case, repeat):
    prefix = "" if manifest.get("command") == "import-cloud" else "model-%d/" % model_index
    return "%s%s-r%d" % (prefix, case, repeat)


def _validate(manifest, records):
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("manifest schema_version must be 1")
    models, cases, repeats = (manifest.get(key) for key in ("models", "cases", "repeats"))
    if (not isinstance(models, list) or not models or not all(isinstance(m, str) and m.strip() for m in models)
            or len(set(models)) != len(models)):
        raise ValueError("invalid models")
    if (not isinstance(cases, list) or not cases or not all(isinstance(c, str) and c in CASE_IDS for c in cases)
            or len(set(cases)) != len(cases) or type(repeats) is not int or repeats not in (1, 2)):
        raise ValueError("invalid case/repeat plan")
    if manifest.get("planned_per_model", len(cases) * repeats) != len(cases) * repeats:
        raise ValueError("inconsistent planned_per_model")
    seen = set()
    for row in records:
        if not isinstance(row, dict) or row.get("model") not in models:
            raise ValueError("unexpected record model")
        phase = row.get("phase")
        if phase != "attempt":
            raise ValueError("unexpected record phase; warmup belongs in metadata.json")
        case, repeat = row.get("case"), row.get("repeat")
        if case not in cases or type(repeat) is not int or repeat not in range(1, repeats + 1):
            raise ValueError("unexpected case/repeat")
        key = (row["model"], case, repeat)
        if key in seen:
            raise ValueError("duplicate attempt")
        seen.add(key)
        if not isinstance(row.get("status"), str) or row.get("status") not in STATUSES:
            raise ValueError("unexpected status")
        metric = row.get("metrics", {})
        if not isinstance(metric, dict):
            raise ValueError("invalid metrics")
        for field in METRICS:
            value = metric.get(field)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError("invalid metric value")
        stem = _stem(manifest, models.index(row["model"]) + 1, case, repeat)
        for field, suffixes in {"raw_response": (".raw.json", ".raw.txt"), "solution": (".solution.py",),
                                "pytest_log": (".pytest.log",), "ps": (".ps.json",)}.items():
            if row.get(field) is not None and row[field] not in [stem + suffix for suffix in suffixes]:
                raise ValueError("unexpected artifact path")


def _environment_lines(env):
    if not isinstance(env, dict):
        return ["- 환경: 미기록 (보고서 재생성 장치로 대체하지 않음)"]
    lines = []
    for group, keys in (("os", ("system", "release", "machine")), ("cpu", ("architecture", "logical_count", "name"))):
        values = env.get(group, {})
        if isinstance(values, dict):
            lines.append("- %s: %s" % (group, "; ".join("%s=%s" % (key, _esc(values.get(key))) for key in keys)))
    for key in ("python_version", "ram_bytes", "ram_unavailable_reason", "nvidia_unavailable_reason"):
        lines.append("- %s: %s" % (key, _esc(env.get(key))))
    if isinstance(env.get("nvidia_gpus"), list):
        for gpu in env["nvidia_gpus"]:
            if isinstance(gpu, dict):
                lines.append("- GPU: " + "; ".join("%s=%s" % (key, _esc(gpu.get(key))) for key in ("name", "memory_total_mib", "driver_version")))
    return lines


EXECUTION_WARNING = ("Generated code runs as the current user with filesystem and network access. "
                     "A temporary directory, Python -I, and a subprocess wall-time limit are not security isolation. "
                     "No RAM, CPU, network, or filesystem isolation is provided. "
                     "Hidden tests and runner output are not protected against adversarial code.")


NOTES = """# 팀 해석 (사람이 작성)

자동 수치·케이스별 증거: [REPORT.md](REPORT.md). 아래 항목은 팀이 직접 작성합니다.

- 모델 카드·라이선스 URL 확인 및 사용 조건 검증: 미완료
- 장치 및 동일 PC 여부: 미완료
- 발견 1 (성공/실패, case ID, REPORT.md의 해당 케이스/증거 링크, 해석): 미완료
- 발견 2 (성공/실패, case ID, REPORT.md의 해당 케이스/증거 링크, 해석): 미완료
- 실행 위험 확인: 생성 코드는 현재 사용자 권한으로 파일시스템과 네트워크에 접근합니다. 임시 디렉터리, Python -I, 시간 제한은 보안 격리가 아닙니다.
- 최종 판단 및 한계: 미완료
- API 키·개인정보·원문 로그 공개 전 점검: 미완료
"""


def write_report(run_dir: Path) -> Path:
    root = Path(run_dir)
    manifest = _read(root / "manifest.json")
    results = root / "results.jsonl"
    if results.is_symlink():
        raise ValueError("symlink input rejected")
    records = [_json(line) for line in results.read_text(encoding="utf-8").splitlines() if line.strip()] if results.exists() else []
    _validate(manifest, records)
    models, cases, repeats = manifest["models"], manifest["cases"], manifest["repeats"]
    summary = summarize(records, models, cases, repeats)
    metadata = {}
    for index, model in enumerate(models, 1):
        file = root / ("model-%d/metadata.json" % index)
        if file.exists():
            if not file.resolve().is_relative_to(root.resolve()):
                raise ValueError("metadata outside run")
            value = _read(file)
            if not isinstance(value, dict) or ("warmup" in value and not isinstance(value["warmup"], dict)):
                raise ValueError("invalid model metadata")
            metadata[model] = value
    for model, item in summary.items():
        item["infra_errors"] = sum(r["status"] in INFRA for r in records if r["model"] == model)
        item["missing_responses"] = item["statuses"].get("missing_response", 0)
        item["run_status"] = manifest.get("run_status")
        item["complete"] = (item["not_run"] == 0 and item["missing_responses"] == 0
                            and manifest.get("run_status") in (None, "completed"))
        item["valid_for_comparison"] = item["complete"] and item["infra_errors"] == 0
    lines = ["# 실행 결과 (자동 생성)", "", "수치는 자동 계산입니다. 해석은 [NOTES.md](NOTES.md)에 사람이 작성해야 하며 이 보고서는 해석 완료를 주장하지 않습니다.", "",
             "서로 다른 PC 간 속도 비교는 의미가 없습니다. 공식 두 모델 동일 PC 비교와 클라우드 5×1 실험은 별도 팀 의무입니다.",
             "결과는 results/<participant>/<run-id> 아래 Git 추적 대상으로 보관합니다. 원문 공개 전 키·개인정보를 확인하세요.", "", "## 실행 정보", "", "Execution warning: " + EXECUTION_WARNING]
    for key in ("participant", "created_utc", "source_commit", "source_dirty", "device_label", "command", "run_status"):
        lines.append("- %s: %s" % (key, _esc(manifest.get(key))))
    if manifest.get("source_dirty") is True:
        lines.append("- 경고: 실행 시 소스 작업 트리가 변경된 상태였습니다. 커밋만으로 재현을 보장하지 않으므로 실제 변경 내용과 suite/prompt 해시를 검토하세요.")
    lines.append("- 요청 모델: " + ", ".join(_esc(model) for model in models))
    lines.append("- 프롬프트·테스트 suite SHA256 및 전체 설정: [manifest.json](manifest.json) (`prompt_sha256`, `suite_sha256`)")
    sources = manifest.get("model_sources", {})
    for model in models:
        source = sources.get(model, {}) if isinstance(sources, dict) else {}
        if not isinstance(source, dict):
            source = {}
        lines.append("- %s 자기보고 모델 카드 URL: %s; 라이선스 URL: %s (팀 검증 필요)" %
                     (_esc(model), _esc(source.get("model_card_url")), _esc(source.get("license_url"))))
    options = manifest.get("options", {})
    evaluator = manifest.get("evaluator", {})
    if not isinstance(options, dict) or not isinstance(evaluator, dict):
        raise ValueError("invalid fixed options")
    lines += ["", "### 고정 옵션"]
    for key in ("num_ctx", "num_predict", "temperature", "seed"):
        lines.append("- %s: %s" % (key, _esc(options.get(key))))
    for key in ("repeat_seeds", "retry_policy", "order", "history", "generation_api", "cloud_controls"):
        lines.append("- %s: %s" % (key, _esc(manifest.get(key))))
    for key in ("backend", "python_version", "pytest_version", "runner_hash", "wall_timeout"):
        lines.append("- Python evaluator %s: %s" % (key, _esc(evaluator.get(key))))
    lines += ["", "### 실행 시 환경"] + _environment_lines(manifest.get("environment"))
    complete = all(item["complete"] for item in summary.values())
    infra = sum(item["infra_errors"] for item in summary.values())
    missing = sum(item["not_run"] + item["missing_responses"] for item in summary.values())
    lines += ["", "## 완료 상태", "전체: %s; 누락 %d; 인프라 오류 %d. %s" %
              ("완료" if complete else "미완료", missing, infra, "경고: 불완전/인프라 오류 결과를 확정 순위로 해석하지 마세요." if not complete or infra else "계획된 기록 수집 완료."),
              "not_run은 미실행이며 실패가 아닙니다. missing_response는 입력 누락입니다. 완료는 모든 풀이 성공을 뜻하지 않습니다.", "",
              "| 모델 | solved/planned | call_successes/attempts | 두 반복 모두 해결/케이스 | 응답 품질 n | 완료 기록 | not_run | 입력 누락 | 인프라 오류 | 상태 |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for model, item in summary.items():
        both = "%d/%d" % (item["all_repeats_solved_cases"], len(cases)) if repeats == 2 else "해당 없음 (1회)"
        lines.append("| %s | %d/%d | %d/%d | %s | %d | %d | %d | %d | %d | %s |" %
                     (_esc(model), item["solved"], item["planned"], item["call_successes"], item["call_attempts"], both,
                      item["successful_response_quality_denominator"], item["completed"], item["not_run"], item["missing_responses"], item["infra_errors"],
                      "완료" if item["valid_for_comparison"] else "경고: 미완료 또는 인프라 오류"))
    lines += ["", "### 성공한 호출의 지표 평균 (각 유효 표본 n)",
              "응답 품질 n은 추출/테스트 실패를 포함한 성공 호출 수입니다. 호출 실패는 평균에서 제외합니다. null은 측정 불가이며 0점이 아닙니다. timeout은 평가 제한시간 초과이며 인프라 오류로 단정하지 않습니다.",
              "| 모델 | elapsed s (n) | loading s (n) | tokens/sec (n) | VRAM MiB (n) |", "|---|---|---|---|---|"]
    for model, item in summary.items():
        cells = []
        for field in METRICS:
            value = item["mean_metrics"][field]
            cells.append(("%.3f" % value["mean"] if value["mean"] is not None else "null") + " (n=%d)" % value["n"])
        lines.append("| " + " | ".join([_esc(model)] + cells) + " |")
    lines += ["", "## Warmup (본 실험 통계에서 제외)"]
    for index, model in enumerate(models, 1):
        warmup = metadata.get(model, {}).get("warmup", {})
        lines.append("- %s: %s; elapsed=%s; %s" % (_esc(model), _esc(warmup.get("status")), _esc(warmup.get("elapsed_seconds")),
                     _link(root, "model-%d/warmup.raw.json" % index, "warmup 원문")))
    lines += ["", "## 케이스별 반복 상태 및 증거", "원문·metadata·show·ps의 내용은 비밀정보 노출 방지를 위해 여기 펼치지 않습니다. 파일이 실제 존재할 때만 링크합니다."]
    for index, model in enumerate(models, 1):
        lines += ["", "### " + _esc(model)]
        refs = [_link(root, "model-%d/%s" % (index, file), label) for file, label in (("metadata.json", "metadata"), ("show.raw.json", "show 원문"))]
        lines.append(" · ".join(filter(None, refs)) or "메타데이터/모델 show: 미기록")
        lines += ["", "| case | repeat | status | 증거 |", "|---|---|---|---|"]
        for case in cases:
            for repeat in range(1, repeats + 1):
                stem = _stem(manifest, index, case, repeat)
                refs = [_link(root, stem + suffix, label) for suffix, label in ((".raw.json", "raw JSON"), (".raw.txt", "raw text"), (".solution.py", "solution"), (".pytest.log", "pytest log"), (".ps.json", "ps"))]
                lines.append("| %s | %d | %s | %s |" % (case, repeat, _esc(summary[model]["per_case"][case][repeat - 1]), " · ".join(filter(None, refs)) or "없음"))
    # All validation/rendering happens before touching previous reports.
    report = "\n".join(lines) + "\n"
    for name in ("summary.json", "REPORT.md", "NOTES.md"):
        if (root / name).is_symlink():
            raise ValueError("symlink output rejected")
    write_json(root / "summary.json", summary)
    atomic_write(root / "REPORT.md", report)
    try:
        with (root / "NOTES.md").open("x", encoding="utf-8") as stream:
            stream.write(NOTES)
    except FileExistsError:
        pass
    return root / "REPORT.md"
