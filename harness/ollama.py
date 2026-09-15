import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .core import atomic_write


class CallFailure(Exception):
    def __init__(self, status, message, elapsed=None):
        super().__init__(message)
        self.status = status
        self.elapsed = elapsed


class Ollama:
    def __init__(self, base_url="http://127.0.0.1:11434", timeout=180):
        parts = urlsplit(base_url)
        if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username
                or parts.password or parts.query or parts.fragment or parts.path not in ("", "/")):
            raise ValueError("Ollama URL must be an HTTP(S) origin without credentials/query/path")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, route, payload=None, raw_path=None):
        request = Request(self.base_url + route,
                          data=json.dumps(payload).encode("utf-8") if payload is not None else None,
                          headers={"Content-Type": "application/json"})
        started = time.monotonic()
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            raw = exc.read()
            if raw_path:
                atomic_write(raw_path, raw)
            raise CallFailure("call_http_error", "HTTP %d" % exc.code, time.monotonic() - started) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise CallFailure("call_transport_error", type(exc).__name__, time.monotonic() - started) from exc
        elapsed = time.monotonic() - started
        if raw_path:
            atomic_write(raw_path, raw)
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise CallFailure("call_invalid_json", "non-JSON response", elapsed) from exc
        if not isinstance(value, dict):
            raise CallFailure("call_invalid_json", "response must be a JSON object", elapsed)
        if value.get("error"):
            raise CallFailure("call_api_error", "Ollama returned an error; see raw log", elapsed)
        return value, elapsed

    def generate(self, model, prompt, options, raw_path, keep_alive="5m"):
        # No context, messages or conversation object is ever reused.
        value, elapsed = self.request("/api/generate", {"model": model, "prompt": prompt,
                                       "stream": False, "options": dict(options),
                                       "keep_alive": keep_alive}, raw_path)
        if value.get("done") is not True or not isinstance(value.get("response"), str):
            raise CallFailure("call_incomplete_response", "missing response text or done=true", elapsed)
        return value, elapsed

    def ps(self, model, raw_path):
        value, _ = self.request("/api/ps")
        if not isinstance(value.get("models"), list):
            raise CallFailure("call_invalid_json", "invalid ps models")
        matched = [m for m in value["models"] if isinstance(m, dict)
                   and model in (m.get("name"), m.get("model"))]
        # Save only this model's server-provided metadata, no environment or credentials.
        filtered = {"models": matched}
        atomic_write(raw_path, json.dumps(filtered, ensure_ascii=False, indent=2))
        return filtered
