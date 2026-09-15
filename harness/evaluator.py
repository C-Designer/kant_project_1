import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import threading
import uuid

from .core import atomic_write

PREFIX = "HARNESS_PYTEST_RESULT="


def docker_preflight(image, timeout=15):
    """Require an available daemon and an already-built image; never pull."""
    def inspect(command, failure):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, timeout=timeout)
        except FileNotFoundError as exc:
            raise ValueError("Docker preflight failed: docker executable not found; install/start Docker and build the evaluator image. No Ollama calls made.") from exc
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Docker preflight failed: " + failure + ". No Ollama calls made.") from exc
        if result.returncode != 0:
            raise ValueError("Docker preflight failed: " + failure + ". No Ollama calls made.")
        return result.stdout.strip()

    version = inspect(["docker", "version", "--format", "{{.Server.Version}}"],
                      "Docker daemon unavailable; start Docker")
    if not version or version in ("<no value>", "null"):
        raise ValueError("Docker preflight failed: missing Docker server version. No Ollama calls made.")
    image_id = inspect(["docker", "image", "inspect", "--format", "{{.Id}}", image],
                       "evaluator image unavailable; build it first with docker build -t " + image + " .")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
        raise ValueError("Docker preflight failed: invalid evaluator image ID. No Ollama calls made.")
    return {"docker_server_version": version, "image_id": image_id, "requested_image": image}


def parse_report(stdout, returncode):
    """Parse fixed trusted pytest runner output, never a solution-created file.

Not tamper-proof against adversarial Python sharing pytest's interpreter.
Docker exit status must agree with the runner's report.
"""
    lines = stdout.rstrip().splitlines()
    if not lines or not lines[-1].startswith(PREFIX):
        raise ValueError("missing final trusted pytest report")
    report = json.loads(lines[-1][len(PREFIX):])
    if not isinstance(report, dict) or report.get("version") != 1:
        raise ValueError("invalid report version")
    if type(report.get("exit_code")) is not int or report["exit_code"] != returncode:
        raise ValueError("Docker exit status and pytest report disagree")
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


def docker_command(name, work, image, timeout=None, memory="512m", cpus=1.0, pids=64):
    return ["docker", "run", "--name", name, "--rm", "--pull", "never", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--pids-limit", str(pids),
            "--memory", memory, "--memory-swap", memory, "--cpus", str(cpus),
            "--user", "65532:65532", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m,mode=1777",
            "--mount", "type=bind,src=%s,dst=/work,readonly" % work,
            "--workdir", "/work", "--env", "PYTHONDONTWRITEBYTECODE=1",
            "--env", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1", "--log-driver", "none",
            "--entrypoint", "python", image, "-I", "/opt/harness/docker_runner.py"]


def run_bounded(command, capture, timeout):
    """Drain stdout continuously, retain only a bounded tail in host memory."""
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    tail = bytearray()
    def drain():
        while True:
            chunk = proc.stdout.read(65536)
            if not chunk:
                break
            tail.extend(chunk)
            if len(tail) > 2 * 1024 * 1024:
                del tail[:-2 * 1024 * 1024]
    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    try:
        proc.wait(timeout=timeout)
    except BaseException:
        proc.kill()
        proc.wait(timeout=5)
        raise
    finally:
        reader.join(timeout=2)
        capture.write(bytes(tail))
    return proc


def evaluate(code, directory, image="kant-harness:1", wall_timeout=30.0,
             memory="512m", cpus=1.0, pids=64, log_path=None):
    started = time.monotonic()
    name = "kant-eval-" + uuid.uuid4().hex
    result = {"status": "evaluator_error", "container": name}
    with tempfile.TemporaryDirectory(prefix="kant-eval-") as temp:
        work = Path(temp)
        work.chmod(0o755)
        atomic_write(work / "solution.py", code)
        for filename in ("test_public.py", "test_hidden.py"):
            shutil.copyfile(Path(directory) / filename, work / filename)
        for file in work.iterdir():
            file.chmod(0o444)
        command = docker_command(name, str(work), image, memory=memory, cpus=cpus, pids=pids)
        # File-backed capture avoids unbounded host RAM use from generated output.
        with tempfile.TemporaryFile() as capture:
            try:
                proc = run_bounded(command, capture, wall_timeout)
                result["docker_exit_code"] = proc.returncode
                capture.seek(0, 2)
                size = capture.tell()
                capture.seek(max(0, size - 2 * 1024 * 1024))
                stdout = capture.read().decode("utf-8", errors="replace")
                if log_path:
                    atomic_write(log_path, stdout)
                if proc.returncode in (125, 126, 127):
                    result["status"] = "docker_error"
                else:
                    try:
                        result.update(parse_report(stdout, proc.returncode))
                        result["status"] = "solved" if result["all_pass"] else "test_failure"
                    except (ValueError, TypeError, KeyError) as exc:
                        result.update(status="evaluator_error", error=str(exc))
            except subprocess.TimeoutExpired:
                result["status"] = "timeout"
            except OSError as exc:
                result.update(status="docker_error", error=str(exc))
            finally:
                # Killing `docker run` alone does not stop the container.
                try:
                    cleanup = subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT, timeout=15)
                    output = cleanup.stdout.decode("utf-8", errors="replace")
                    if cleanup.returncode and "No such container" not in output:
                        result["cleanup_error"] = output[-2000:]
                except (OSError, subprocess.TimeoutExpired) as exc:
                    result["cleanup_error"] = str(exc)
        result["evaluation_elapsed_seconds"] = time.monotonic() - started
    return result
