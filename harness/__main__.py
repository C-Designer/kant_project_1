import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
import time

from .core import (CASE_IDS, CLOUD_IDS, ExtractionError, append_jsonl, atomic_write,
                   build_prompt, case_path, extract_python, metrics, sha256, summarize, write_json)
from .evaluator import docker_preflight, evaluate
from .ollama import CallFailure, Ollama

NOTICE = ("Resource isolation only, not an adversarially secure sandbox. Hidden tests are excluded "
          "from prompts, but generated code can inspect the read-only test mount and shares pytest's "
          "interpreter. Reports are produced by the fixed pytest runner and parsed by the host, "
          "not read from model-written result files.")


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be positive and finite")
    return number


def temperature(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative and finite")
    return number


def memory_limit(value):
    if not re.fullmatch(r"[1-9][0-9]*[kKmMgG]", value):
        raise argparse.ArgumentTypeError("use a positive memory limit, e.g. 512m")
    return value


def full_tag(value):
    if ":" not in value.rsplit("/", 1)[-1] or value.startswith("-") or any(c.isspace() for c in value):
        raise argparse.ArgumentTypeError("supply the full Ollama tag, e.g. qwen2.5-coder:7b")
    return value


def add_eval_args(parser):
    parser.add_argument("--image", default="kant-harness:1")
    parser.add_argument("--wall-timeout", type=positive_float, default=30.0)
    parser.add_argument("--memory", type=memory_limit, default="512m")
    parser.add_argument("--cpus", type=positive_float, default=1.0)
    parser.add_argument("--pids", type=positive_int, default=64)


def parser():
    root = argparse.ArgumentParser(description="Independent first-response coding benchmark. " + NOTICE)
    commands = root.add_subparsers(dest="command", required=True)
    local = commands.add_parser("run", help="two Ollama models x ten cases x two attempts")
    local.add_argument("--models", nargs=2, required=True, type=full_tag)
    local.add_argument("--url", default="http://127.0.0.1:11434")
    local.add_argument("--call-timeout", type=positive_float, default=180.0)
    local.add_argument("--num-ctx", type=positive_int, default=8192)
    local.add_argument("--num-predict", type=positive_int, default=2048)
    local.add_argument("--temperature", type=temperature, default=0.2)
    local.add_argument("--seed", type=int, default=42, help="repeat seeds are seed and seed+1")
    verify = commands.add_parser("verify-cases", help="references pass; starters fail at least one hidden test")
    export = commands.add_parser("export-cloud", help="fixed five-case subset; independent manual calls")
    export.add_argument("--repeats", type=int, choices=(1,), default=1,
                        help="fixed at one first-response attempt per cloud case")
    cloud = commands.add_parser("import-cloud", help="import B01-r1.txt etc.; never call a cloud API")
    cloud.add_argument("--bundle", required=True, type=Path)
    cloud.add_argument("--responses", required=True, type=Path)
    cloud.add_argument("--model", required=True, help="record the provider and exact displayed model/version")
    for sub in (local, verify, export, cloud):
        sub.add_argument("--cases", type=Path, default=Path("cases"))
        sub.add_argument("--out", type=Path, required=True, help="new output directory; existing paths rejected")
    for sub in (local, verify, cloud):
        add_eval_args(sub)
    summary = commands.add_parser("summarize")
    summary.add_argument("run_directory", type=Path)
    extraction = commands.add_parser("extract", help="extract code without importing or executing it")
    extraction.add_argument("raw_text", type=Path)
    extraction.add_argument("--out", type=Path, required=True)
    return root


def suite_fingerprints(root, ids):
    result = {}
    for case in ids:
        directory = case_path(root, case)
        result[case] = {name: sha256((directory / name).read_text(encoding="utf-8"))
                        for name in ("prompt.md", "starter.py", "reference.py", "test_public.py", "test_hidden.py")}
    return result


def start_run(args, ids, models, repeats, prompts):
    fingerprints = suite_fingerprints(args.cases, ids)
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                "command": args.command, "models": models, "cases": list(ids), "repeats": repeats,
                "planned_per_model": len(ids) * repeats, "suite_sha256": fingerprints,
                "prompt_sha256": {case: sha256(text) for case, text in prompts.items()},
                "sandbox_notice": NOTICE, "retry_policy": "none", "order": "model, case, repeat"}
    if hasattr(args, "image"):
        manifest["evaluator"] = {k: getattr(args, k) for k in ("image", "wall_timeout", "memory", "cpus", "pids")}
    write_json(args.out / "manifest.json", manifest)
    return manifest


def eval_code(args, code, case, stem):
    return evaluate(code, case_path(args.cases, case), image=getattr(args, "eval_image_id", args.image), wall_timeout=args.wall_timeout,
                    memory=args.memory, cpus=args.cpus, pids=args.pids,
                    log_path=args.out / (stem + ".pytest.log"))


def response_result(args, text, case, stem):
    try:
        code = extract_python(text)
    except ExtractionError as exc:
        return {"status": "extraction_failure", "error": str(exc)}
    atomic_write(args.out / (stem + ".solution.py"), code)
    evaluation = eval_code(args, code, case, stem)
    return {"status": evaluation["status"], "evaluation": evaluation, "solution_sha256": sha256(code)}


def finish(args, records, manifest):
    summary = summarize(records, manifest["models"], manifest["cases"], manifest["repeats"])
    write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


def run_local(args):
    if len(set(args.models)) != 2:
        raise ValueError("two distinct model tags required")
    docker_metadata = docker_preflight(args.image)
    args.eval_image_id = docker_metadata["image_id"]
    client = Ollama(args.url, args.call_timeout)
    prompts = {case: build_prompt(args.cases, case) for case in CASE_IDS}
    manifest = start_run(args, CASE_IDS, args.models, 2, prompts)
    manifest["evaluator"].update(docker_metadata)
    options = {"num_ctx": args.num_ctx, "num_predict": args.num_predict,
               "temperature": args.temperature, "seed": args.seed}
    manifest.update(options=options, repeat_seeds=[args.seed, args.seed + 1], endpoint=args.url,
                    generation_api="/api/generate", history="reset each request; no context sent")
    write_json(args.out / "manifest.json", manifest)
    records = []
    for index, model in enumerate(args.models, 1):
        model_dir = args.out / ("model-%d" % index)
        model_dir.mkdir()
        metadata = {"requested_full_tag": model}
        try:
            show, _ = client.request("/api/show", {"model": model}, model_dir / "show.raw.json")
            metadata["show"] = show
        except CallFailure as exc:
            metadata["show_error"] = {"status": exc.status, "error": str(exc)}
        try:
            warmup, elapsed = client.generate(model, "Reply with OK.", options, model_dir / "warmup.raw.json")
            metadata["warmup"] = {"phase": "warmup", "status": "ok", "elapsed_seconds": elapsed}
        except CallFailure as exc:
            metadata["warmup"] = {"phase": "warmup", "status": exc.status, "error": str(exc)}
        write_json(model_dir / "metadata.json", metadata)
        try:
            for case in CASE_IDS:
                for repeat in (1, 2):
                    stem = "model-%d/%s-r%d" % (index, case, repeat)
                    attempt_options = dict(options, seed=args.seed + repeat - 1)
                    row = {"phase": "attempt", "model": model, "case": case, "repeat": repeat,
                           "options": attempt_options, "prompt_sha256": sha256(prompts[case]),
                           "raw_response": stem + ".raw.json"}
                    try:
                        response, elapsed = client.generate(model, prompts[case], attempt_options,
                                                            args.out / row["raw_response"])
                        row["response_model"] = response.get("model")
                        ps = None
                        try:
                            ps = client.ps(model, args.out / (stem + ".ps.json"))
                        except CallFailure as exc:
                            row["ps_error"] = {"status": exc.status, "error": str(exc)}
                        row["metrics"] = metrics(response, elapsed, ps, model)
                        row.update(response_result(args, response["response"], case, stem))
                    except CallFailure as exc:
                        row.update(status=exc.status, error=str(exc), metrics=metrics({}, exc.elapsed))
                        if not (args.out / row["raw_response"]).exists():
                            row["raw_response"] = None  # no server bytes were received
                    records.append(row)
                    append_jsonl(args.out / "results.jsonl", row)
                    print("%s %s r%d: %s" % (model, case, repeat, row["status"]), file=sys.stderr)
        finally:
            # Explicitly unload this benchmark model before starting the next; not an attempt/retry.
            try:
                client.request("/api/generate", {"model": model, "stream": False, "keep_alive": 0},
                               model_dir / "unload.raw.json")
            except CallFailure as exc:
                write_json(model_dir / "unload.error.json", {"status": exc.status, "error": str(exc)})
    return finish(args, records, manifest)


def verify_cases(args):
    start_run(args, CASE_IDS, ["reference", "starter"], 1, {})
    good = True
    for case in CASE_IDS:
        directory = case_path(args.cases, case)
        reference = eval_code(args, (directory / "reference.py").read_text(encoding="utf-8"), case, case + "-reference")
        starter = eval_code(args, (directory / "starter.py").read_text(encoding="utf-8"), case, case + "-starter")
        hidden = starter.get("groups", {}).get("hidden", {})
        valid = (reference["status"] == "solved" and starter["status"] == "test_failure"
                 and hidden.get("failed", 0) >= 1 and not starter.get("collection_errors"))
        row = {"case": case, "valid": valid, "reference": reference, "starter": starter}
        append_jsonl(args.out / "verification.jsonl", row)
        good = good and valid
        print(json.dumps(row))
    write_json(args.out / "verification_summary.json", {"all_valid": good, "cases": 10})
    return 0 if good else 1


def export_cloud(args):
    if type(args.repeats) is not int or args.repeats != 1:
        raise ValueError("cloud export requires exactly one repeat per case")
    prompts = {case: build_prompt(args.cases, case) for case in CLOUD_IDS}
    # Cloud bundle includes ONLY prompt-visible content and hashes, never hidden/reference text.
    args.out.mkdir(parents=True, exist_ok=False)
    bundle = {"schema_version": 1, "cases": list(CLOUD_IDS), "repeats": args.repeats,
              "selection": "fixed pre-experiment: B01 B04 B06 B08 B10", "independent_first_response": True,
              "prompt_sha256": {case: sha256(text) for case, text in prompts.items()},
              "instructions": "Use a fresh conversation for every repeat. Save the complete first response as "
                              "B01-r1.txt etc. No edits, retries, followups, or repair. Record provider/model "
                              "version separately. Cloud sampling controls may not equal Ollama controls; "
                              "this is a separate supplemental comparison, not the main ranking."}
    for case, text in prompts.items():
        atomic_write(args.out / (case + ".prompt.txt"), text)
        for repeat in range(1, args.repeats + 1):
            append_jsonl(args.out / "requests.jsonl", {"case": case, "repeat": repeat,
                         "prompt": case + ".prompt.txt", "response_filename": "%s-r%d.txt" % (case, repeat)})
    write_json(args.out / "bundle.json", bundle)
    print(json.dumps(bundle, indent=2))
    return 0


def import_cloud(args):
    bundle = json.loads((args.bundle / "bundle.json").read_text(encoding="utf-8"))
    if bundle.get("schema_version") != 1 or bundle.get("cases") != list(CLOUD_IDS):
        raise ValueError("cloud bundle must use the fixed five IDs")
    repeats = bundle.get("repeats")
    if type(repeats) is not int or repeats != 1:
        raise ValueError("cloud bundle must contain exactly one repeat per case")
    prompts = {case: build_prompt(args.cases, case) for case in CLOUD_IDS}
    for case, text in prompts.items():
        exported = (args.bundle / (case + ".prompt.txt")).read_text(encoding="utf-8")
        if sha256(text) != bundle["prompt_sha256"].get(case) or text != exported:
            raise ValueError("prompt drift for " + case)
    manifest = start_run(args, CLOUD_IDS, [args.model], repeats, prompts)
    manifest["cloud_controls"] = "manual independent first-response import; timing/tokens/sampling unverified"
    write_json(args.out / "manifest.json", manifest)
    records = []
    for case in CLOUD_IDS:
        for repeat in range(1, repeats + 1):
            stem = "%s-r%d" % (case, repeat)
            source = args.responses / (stem + ".txt")
            row = {"phase": "attempt", "model": args.model, "case": case, "repeat": repeat,
                   "source": "cloud_import", "prompt_sha256": sha256(prompts[case]), "metrics": metrics({})}
            try:
                raw = source.read_bytes()
            except FileNotFoundError:
                row["status"] = "missing_response"
            else:
                atomic_write(args.out / (stem + ".raw.txt"), raw)
                row["raw_response"] = stem + ".raw.txt"
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    row["status"] = "invalid_response_encoding"
                else:
                    row.update(response_result(args, text, case, stem))
            append_jsonl(args.out / "results.jsonl", row)
            records.append(row)
    return finish(args, records, manifest)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "run":
            return run_local(args)
        if args.command == "verify-cases":
            return verify_cases(args)
        if args.command == "export-cloud":
            return export_cloud(args)
        if args.command == "import-cloud":
            return import_cloud(args)
        if args.command == "extract":
            if args.out.exists():
                raise ValueError("output already exists")
            atomic_write(args.out, extract_python(args.raw_text.read_text(encoding="utf-8")))
            return 0
        if args.command == "summarize":
            manifest = json.loads((args.run_directory / "manifest.json").read_text(encoding="utf-8"))
            results_path = args.run_directory / "results.jsonl"
            records = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()] if results_path.exists() else []
            print(json.dumps(summarize(records, manifest["models"], manifest["cases"], manifest["repeats"]), indent=2))
            return 0
    except (OSError, ValueError, KeyError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted; finished attempts remain in results.jsonl", file=sys.stderr)
        return 130
    return 2


if __name__ == "__main__":
    sys.exit(main())
