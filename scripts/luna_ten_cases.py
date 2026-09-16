"""Call gpt-5.6-luna on the ten harness cases, using the same call settings as the
class-provided 02_luna_chat.py. Each call is an independent first response.

Usage: python runs/03_luna_ten_cases.py <repeat> [case ...]

The key is read from .env (gitignored) and never printed. Responses land in
runs/luna-responses/ as BXX-rN.txt plus the provider's raw JSON.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import APIError, APITimeoutError, OpenAI

from harness.core import CASE_IDS, build_prompt

MODEL = "gpt-5.6-luna"
CASES_ROOT = Path("cases")
OUT_DIR = Path("runs/luna-responses")


def load_key():
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == "OPENAI_API_KEY":
            return value.strip()
    raise SystemExit("OPENAI_API_KEY not found in .env")


def main(repeat, cases):
    client = OpenAI(api_key=load_key(), base_url="https://api.openai.com/v1",
                    timeout=120, max_retries=0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for case in cases:
        stem = "%s-r%d" % (case, repeat)
        start = time.monotonic()
        try:
            response = client.responses.create(
                model=MODEL, input=build_prompt(CASES_ROOT, case), reasoning={"effort": "none"},
                max_output_tokens=2048, tools=[], tool_choice="none", store=False,
            )
        except APITimeoutError:
            print("%s: timeout" % case)
            continue
        except APIError as error:
            print("%s: api error %s" % (case, getattr(error, "status_code", error)))
            continue
        elapsed = time.monotonic() - start
        (OUT_DIR / (stem + ".txt")).write_text(response.output_text or "", encoding="utf-8")
        raw = response.model_dump()
        (OUT_DIR / (stem + ".raw.json")).write_text(
            json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        usage = raw.get("usage") or {}
        print("%s r%d: %s %.1fs in=%s out=%s" % (case, repeat, response.status, elapsed,
                                                 usage.get("input_tokens"), usage.get("output_tokens")))


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2:] or CASE_IDS)
