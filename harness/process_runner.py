"""Fixed local pytest entrypoint. Not a sandbox or tamper-proof judge.

Candidate code shares pytest's interpreter and can access the filesystem/network.
"""
import json
import sys
import os
from pathlib import Path
import pytest

PREFIX = "HARNESS_PYTEST_RESULT="


class Results:
    def __init__(self):
        self.tests = {}
        self.collection_errors = []

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append(report.nodeid)

    def pytest_runtest_logreport(self, report):
        entry = self.tests.setdefault(report.nodeid, {"nodeid": report.nodeid, "outcome": "passed"})
        if report.failed:
            entry["outcome"] = "failed" if report.when == "call" else "error"
        elif report.skipped and entry["outcome"] == "passed":
            entry["outcome"] = "skipped"


def main():
    sys.path.insert(0, os.getcwd())
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    plugin = Results()
    exit_code = int(pytest.main(["-q", "-s", "--rootdir", os.getcwd(), "-c", str(Path(__file__).with_name("pytest.ini")), "--import-mode=importlib",
                                "-p", "no:cacheprovider", "--tb=short",
                                "--confcutdir", os.getcwd(), "--noconftest",
                                "test_public.py", "test_hidden.py"], plugins=[plugin]))
    payload = {"version": 1, "exit_code": exit_code, "tests": list(plugin.tests.values()),
               "collection_errors": plugin.collection_errors}
    print("\n" + PREFIX + json.dumps(payload, sort_keys=True), flush=True)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
