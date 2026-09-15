"""Local Python evaluation, NOT a sandbox.

Code can access the user's filesystem and network. Environment filtering and
process-group cleanup do not provide filesystem, network, or memory isolation.
Only evaluate code that the operator has authorized to run locally.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace

from .core import atomic_write

PREFIX = "HARNESS_PYTEST_RESULT="
OUTPUT_LIMIT = 2 * 1024 * 1024
RUNNER = Path(__file__).with_name("process_runner.py").resolve()
# No inherited PATH, HOME, Python/pytest options, proxy settings, or API tokens.
ENV_ALLOWLIST = ("SYSTEMROOT", "WINDIR", "COMSPEC", "LANG", "LC_ALL", "LC_CTYPE",
                 "TMPDIR", "TMP", "TEMP")


def process_environment():
    env = {key: value for key, value in os.environ.items()
           if key.upper() in ENV_ALLOWLIST}
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return env


def python_preflight():
    """Check pytest using this interpreter before any model request.

    Return portable version/hash metadata, never an interpreter's personal path.
    """
    command = [sys.executable, "-I", "-c",
               "import json,platform,pytest; print(json.dumps({"
               "'python_version':platform.python_version(),"
               "'pytest_version':pytest.__version__}))"]
    try:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=15, env=process_environment())
        if proc.returncode != 0:
            raise ValueError("pytest import failed")
        metadata = json.loads(proc.stdout)
        if not isinstance(metadata, dict) or not all(
            isinstance(metadata.get(k), str) and metadata[k].strip()
            for k in ("python_version", "pytest_version")
        ):
            raise ValueError("invalid interpreter metadata")
        return {"backend": "python-subprocess",
                "python_version": metadata["python_version"],
                "pytest_version": metadata["pytest_version"],
                "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest()}
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError) as exc:
        raise ValueError("Python preflight failed: pytest must be installed in the current "
                         "Python 3.12 environment. No model calls made.") from exc


def process_command():
    return [sys.executable, "-I", "-B", str(RUNNER)]


def parse_report(stdout, returncode):
    """Parse fixed trusted pytest runner output, never a solution-created file.

Not tamper-proof against adversarial Python sharing pytest's interpreter.
Process exit status must agree with the runner's report.
"""
    lines = stdout.rstrip().splitlines()
    if not lines or not lines[-1].startswith(PREFIX):
        raise ValueError("missing final trusted pytest report")
    report = json.loads(lines[-1][len(PREFIX):])
    if not isinstance(report, dict) or report.get("version") != 1:
        raise ValueError("invalid report version")
    if type(report.get("exit_code")) is not int or report["exit_code"] != returncode:
        raise ValueError("Process exit status and pytest report disagree")
    tests, errors = report.get("tests"), report.get("collection_errors")
    if not isinstance(tests, list) or not isinstance(errors, list) or not all(isinstance(e, str) for e in errors):
        raise ValueError("invalid test report")
    groups = {"public": {k: 0 for k in ("passed", "failed", "error", "skipped")},
              "hidden": {k: 0 for k in ("passed", "failed", "error", "skipped")}}
    seen = set()
    for test in tests:
        if not isinstance(test, dict):
            raise ValueError("invalid test entry")
        node, outcome = test.get("nodeid"), test.get("outcome")
        if not isinstance(node, str) or node in seen or outcome not in groups["public"]:
            raise ValueError("invalid or duplicate test")
        seen.add(node)
        filename = node.split("::", 1)[0].rsplit("/", 1)[-1]
        group = {"test_public.py": "public", "test_hidden.py": "hidden"}.get(filename)
        if group is None:
            raise ValueError("unexpected test filename")
        groups[group][outcome] += 1
    all_pass = returncode == 0 and not errors and all(
        values["passed"] > 0 and not any(values[k] for k in ("failed", "error", "skipped"))
        for values in groups.values())
    return {"pytest_exit_code": returncode, "groups": groups, "collection_errors": errors,
            "test_count": len(tests), "all_pass": all_pass}


def _kill_tree(proc):
    """Kill the POSIX process group; best-effort Windows tree cleanup.

    Deliberately detached descendants can escape this, so this is not a sandbox.
    """
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        root = os.environ.get("SystemRoot", os.environ.get("SYSTEMROOT", r"C:\Windows"))
        try:
            subprocess.run([str(Path(root) / "System32" / "taskkill.exe"),
                            "/PID", str(proc.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=5, env=process_environment())
        except (OSError, subprocess.TimeoutExpired):
            pass
    if proc.poll() is None:
        proc.kill()


def run_bounded(command, work, timeout):
    """Drain output without unbounded storage and stop ordinary descendants."""
    kwargs = {"start_new_session": True} if os.name == "posix" else {
        "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    proc = subprocess.Popen(command, cwd=work, env=process_environment(),
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, bufsize=0, **kwargs)
    tail = bytearray()
    lock = threading.Lock()
    stopped = threading.Event()
    if os.name == "posix":
        os.set_blocking(proc.stdout.fileno(), False)

    def drain():
        try:
            while not stopped.is_set():
                try:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                except BlockingIOError:
                    stopped.wait(0.01)
                    continue
                if not chunk:
                    break
                with lock:
                    tail.extend(chunk)
                    if len(tail) > OUTPUT_LIMIT:
                        del tail[:-OUTPUT_LIMIT]
        except (OSError, ValueError):
            pass

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    timed_out = False
    try:
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
    finally:
        # Run even after a clean pytest exit: tests may have left children behind.
        _kill_tree(proc)
        proc.wait(timeout=5)
        reader.join(timeout=1)
        stopped.set()
        # Raw FileIO closure does not acquire a buffered-reader lock.
        proc.stdout.close()
        reader.join(timeout=1)
    with lock:
        output = bytes(tail).decode("utf-8", errors="replace")
    return SimpleNamespace(returncode=proc.returncode, stdout=output, timed_out=timed_out)


def evaluate(code, directory, wall_timeout=30.0, log_path=None):
    """Run locally in a disposable cwd. This grants filesystem/network access."""
    started = time.monotonic()
    result = {"status": "evaluator_error", "backend": "python-subprocess",
              "process_exit_code": None,
              "groups": {group: {key: 0 for key in ("passed", "failed", "error", "skipped")}
                         for group in ("public", "hidden")},
              "collection_errors": [], "test_count": 0, "all_pass": False}
    try:
        if isinstance(wall_timeout, bool) or not isinstance(wall_timeout, (int, float)) or not (
            math.isfinite(wall_timeout) and wall_timeout > 0
        ):
            raise ValueError("wall_timeout must be a finite positive number")
        with tempfile.TemporaryDirectory(prefix="kant-eval-") as temp:
            work = Path(temp)
            atomic_write(work / "solution.py", code)
            for filename in ("test_public.py", "test_hidden.py"):
                shutil.copyfile(Path(directory) / filename, work / filename)
            proc = run_bounded(process_command(), work, wall_timeout)
            result["process_exit_code"] = proc.returncode
            if log_path:
                atomic_write(log_path, proc.stdout)
            if proc.timed_out:
                result["status"] = "timeout"
            else:
                result.update(parse_report(proc.stdout, proc.returncode))
                result["status"] = "solved" if result["all_pass"] else "test_failure"
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        # Do not publish exception text containing personal absolute paths.
        result.update(status="evaluator_error", error="Evaluation failed: " + type(exc).__name__)
    finally:
        result["evaluation_elapsed_seconds"] = time.monotonic() - started
    return result
