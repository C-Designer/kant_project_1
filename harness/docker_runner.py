"""Trusted image entrypoint, never executed on the host by the harness.

This is resource isolation, NOT a sandbox secure against adversarial Python.
Generated Python shares an interpreter with pytest and can see mounted tests.
"""
import json
import sys
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
    sys.path.insert(0, "/work")
    plugin = Results()
    exit_code = int(pytest.main(["-q", "-c", "/opt/harness/pytest.ini", "--import-mode=importlib",
                                "-p", "no:cacheprovider", "--tb=short",
                                "/work/test_public.py", "/work/test_hidden.py"], plugins=[plugin]))
    payload = {"version": 1, "exit_code": exit_code, "tests": list(plugin.tests.values()),
               "collection_errors": plugin.collection_errors}
    print("\n" + PREFIX + json.dumps(payload, sort_keys=True), flush=True)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
