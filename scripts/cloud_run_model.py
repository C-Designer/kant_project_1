"""Full 10-case x2-repeat cloud API run, producing the same layout as `harness run-model`
(results/<participant>/<run-id>/ with manifest.json, results.jsonl, summary.json, REPORT.md,
NOTES.md, model-1/...).

NOT the team's official Cloud protocol: docs/CLOUD.md fixes the Cloud comparison at 5 calls
total (B01/B04/B06/B08/B10, one each) specifically to bound API cost. Running the full local-style
20-call protocol against a paid cloud model is a deliberate deviation from that agreed design and
costs roughly 4x as much. Any results produced by this script should be flagged as non-official
until the team reviews and accepts the change in protocol.

Each case/repeat is one fresh, non-retried request (no conversation history reused), matching the
project's no-repair-loop rule. The API key is read only from the LUNA_API_KEY environment variable
and is never written to any output file or logged.

Usage:
    uv run python scripts/cloud_run_model.py --participant cloud --model gpt-5.6-luna \
        --run-id 20260916-gpt5-6-luna --device-label cloud-api

Set LUNA_API_BASE if the endpoint is not the standard https://api.openai.com/v1.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.core import CASE_IDS, atomic_write, build_prompt, metrics, sha256, write_json  # noqa: E402
from harness.reporting import capture_environment  # noqa: E402
from harness.__main__ import (evaluator_preflight, finish, response_result,  # noqa: E402
                               safe_id, source_state, start_run)


def call_once(base_url, api_key, model, prompt, max_tokens, timeout):
    # This model rejects any non-default temperature (HTTP 400 "Only the default (1) value is
    # supported"), so temperature is intentionally omitted rather than forced to a fixed value.
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "max_completion_tokens": max_tokens}
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key},
        method="POST")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        return {"status": "call_http_error", "http_status": exc.code,
                "body": exc.read().decode("utf-8", errors="replace"),
                "elapsed_seconds": time.monotonic() - started}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"status": "call_transport_error", "error": type(exc).__name__,
                "elapsed_seconds": time.monotonic() - started}
    elapsed = time.monotonic() - started
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return {"status": "call_invalid_json", "elapsed_seconds": elapsed}
    try:
        text = value["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return {"status": "call_api_error", "error": "missing choices[0].message.content",
                "raw_response": value, "elapsed_seconds": elapsed}
    return {"status": "ok", "text": text, "raw_response": value, "elapsed_seconds": elapsed}


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--participant", required=True, type=safe_id)
    p.add_argument("--model", required=True, help="exact cloud model id, e.g. gpt-5.6-luna")
    p.add_argument("--run-id", type=safe_id)
    p.add_argument("--results-root", type=Path, default=Path("results"))
    p.add_argument("--device-label", default="cloud-api")
    p.add_argument("--model-card-url")
    p.add_argument("--license-url")
    p.add_argument("--cases", type=Path, default=Path("cases"))
    p.add_argument("--max-tokens", type=int, default=2048)
    p.add_argument("--timeout", type=float, default=180.0)
    p.add_argument("--wall-timeout", type=float, default=30.0)
    return p


def main():
    args = parser().parse_args()
    if not args.model or any(c.isspace() for c in args.model):
        raise SystemExit("--model must be a non-empty, whitespace-free model id")
    api_key = os.environ.get("LUNA_API_KEY")
    if not api_key:
        raise SystemExit("set LUNA_API_KEY in your own shell before running this script")
    base_url = os.environ.get("LUNA_API_BASE", "https://api.openai.com/v1")

    run_id = args.run_id or (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ").lower()
                             + "-" + os.urandom(4).hex())
    args.out = args.results_root / args.participant / run_id
    args.models = [args.model]
    args.command = "run-model"
    args.evaluator_metadata = evaluator_preflight()

    environment = capture_environment()
    provenance = source_state()
    prompts = {case: build_prompt(args.cases, case) for case in CASE_IDS}
    manifest = start_run(args, CASE_IDS, args.models, 2, prompts)
    manifest.update(environment=environment, **provenance)
    manifest.update(participant=args.participant, device_label=args.device_label,
                    model_card_url=args.model_card_url, license_url=args.license_url,
                    metadata_provenance="participant, device_label, model_card_url and license_url "
                                        "are user supplied; unverified")
    manifest["model_sources"] = {args.model: {"model_card_url": args.model_card_url,
                                              "license_url": args.license_url,
                                              "provenance": "user supplied; unverified"}}
    manifest.update(run_status="in_progress", completed_attempts=0, planned_attempts=len(CASE_IDS) * 2)
    options = {"num_ctx": None, "num_predict": args.max_tokens, "temperature": None, "seed": None}
    manifest.update(options=options, repeat_seeds=[None, None], endpoint=base_url,
                    generation_api="/chat/completions", history="reset each request; no context sent",
                    cloud_controls="OpenAI-compatible chat completions API; no local seed control. "
                                    "This model rejects any non-default temperature (HTTP 400), so "
                                    "temperature is not sent and the model's own default applies. "
                                    "This run uses the full 10-case x2-repeat local-style protocol, "
                                    "NOT the team's fixed 5-call Cloud comparison in docs/CLOUD.md.")
    write_json(args.out / "manifest.json", manifest)

    model = args.model
    model_dir = args.out / "model-1"
    model_dir.mkdir()
    write_json(model_dir / "metadata.json", {"requested_full_tag": model})

    records = []
    try:
        for case in CASE_IDS:
            for repeat in (1, 2):
                stem = "model-1/%s-r%d" % (case, repeat)
                row = {"phase": "attempt", "model": model, "case": case, "repeat": repeat,
                       "prompt_sha256": sha256(prompts[case]), "raw_response": stem + ".raw.json"}
                result = call_once(base_url, api_key, model, prompts[case], args.max_tokens, args.timeout)
                atomic_write(args.out / row["raw_response"],
                            json.dumps({k: v for k, v in result.items() if k != "text"},
                                       ensure_ascii=False, indent=2))
                if result["status"] == "ok":
                    row["response_model"] = result.get("raw_response", {}).get("model")
                    row["metrics"] = metrics({}, elapsed_seconds=result["elapsed_seconds"])
                    row.update(response_result(args, result["text"], case, stem))
                else:
                    row.update(status=result["status"], error=result.get("error") or result.get("body"),
                               metrics=metrics({}, elapsed_seconds=result["elapsed_seconds"]))
                records.append(row)
                with (args.out / "results.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                print("%s %s r%d: %s" % (model, case, repeat, row["status"]), file=sys.stderr)
    except BaseException as exc:
        manifest.update(run_status="interrupted" if isinstance(exc, KeyboardInterrupt) else "incomplete",
                        completed_attempts=len(records), failure_type=type(exc).__name__)
        write_json(args.out / "manifest.json", manifest)
        finish(args, records, manifest)
        raise
    manifest.update(run_status="completed", completed_attempts=len(records))
    write_json(args.out / "manifest.json", manifest)
    return finish(args, records, manifest)


if __name__ == "__main__":
    sys.exit(main())
