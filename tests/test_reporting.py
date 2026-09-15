import json
import subprocess

import pytest

from harness.core import CASE_IDS, CLOUD_IDS
from harness.reporting import capture_environment, write_report


def fixture_run(tmp_path, models=None, records=()):
    manifest = {"schema_version": 1, "models": models or ["model:1"], "cases": list(CASE_IDS),
                "repeats": 2, "planned_per_model": 20, "participant": "synthetic",
                "created_utc": "2026-01-01T00:00:00Z", "source_commit": "abc123", "source_dirty": True,
                "device_label": "test PC", "command": "run", "options": {"seed": 42},
                "evaluator": {"image_id": "sha256:test"}}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    if records:
        save_rows(tmp_path, records)
    return manifest


def save_rows(root, rows):
    (root / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows))


def row(case="B01", repeat=1, status="solved", **extra):
    return {"phase": "attempt", "model": "model:1", "case": case, "repeat": repeat,
            "status": status, **extra}


def summary(root):
    return json.loads((root / "summary.json").read_text())["model:1"]


def test_empty_plan_is_not_failure(tmp_path):
    fixture_run(tmp_path)
    report = write_report(tmp_path)
    data = summary(tmp_path)
    assert data["planned"] == 20 and data["completed"] == 0
    assert data["not_run"] == 20 and data["call_failures"] == 0
    assert not data["complete"]
    assert "미완료" in report.read_text()
    assert "null (n=0)" in report.read_text()
    assert "0/20" in report.read_text()
    assert "0/10" in report.read_text()


def test_twenty_planned_solved(tmp_path):
    fixture_run(tmp_path, records=[row(case, repeat) for case in CASE_IDS for repeat in (1, 2)])
    text = write_report(tmp_path).read_text()
    data = summary(tmp_path)
    assert data["solved"] == 20 and data["all_repeats_solved_cases"] == 10
    assert data["complete"] and data["valid_for_comparison"]
    assert "20/20" in text and "10/10" in text
    assert all(case in text for case in CASE_IDS)
    assert "sha256:test" in text


def test_failure_and_success_denominators(tmp_path):
    fixture_run(tmp_path, records=[
        row(metrics={"elapsed_seconds": 2, "tokens_per_second": 10, "load_duration_seconds": 0, "vram_mib": 0}),
        row(repeat=2, status="extraction_failure", metrics={"elapsed_seconds": 4}),
        row("B02", status="call_transport_error", metrics={"elapsed_seconds": 100}),
        row("B02", 2, "docker_error"), row("B03", 1, "missing_response")])
    write_report(tmp_path)
    data = summary(tmp_path)
    assert data["call_successes"] == 3 and data["call_attempts"] == 5
    assert data["successful_response_quality_denominator"] == 3
    assert data["infra_errors"] == 2 and data["missing_responses"] == 1
    assert data["not_run"] == 15
    assert data["mean_metrics"]["elapsed_seconds"] == {"mean": 3, "n": 2}
    assert data["mean_metrics"]["load_duration_seconds"] == {"mean": 0, "n": 1}


def test_zero_valid_metrics(tmp_path):
    fixture_run(tmp_path, records=[row(metrics={key: None for key in
        ("elapsed_seconds", "load_duration_seconds", "tokens_per_second", "vram_mib")})])
    write_report(tmp_path)
    assert all(value == {"mean": None, "n": 0} for value in summary(tmp_path)["mean_metrics"].values())


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(model="unknown"), lambda r: r.update(case="B11"),
    lambda r: r.update(repeat=True), lambda r: r.update(repeat=3),
    lambda r: r.update(status="not_run"), lambda r: r.update(status="unexpected"),
    lambda r: r.update(phase="warmup"), lambda r: r.update(metrics=[]),
    lambda r: r.update(metrics={"elapsed_seconds": -1}),
    lambda r: r.update(metrics={"tokens_per_second": "12"}),
    lambda r: r.update(raw_response="../secrets.json"),
    lambda r: r.update(raw_response="https://example.com/secret"),
    lambda r: r.update(raw_response="model-2/B01-r1.raw.json"),
    lambda r: r.update(raw_response="model-1/B01-r1.raw.json)\n[evil](x"),
])
def test_reject_bad_rows_preserve_outputs(tmp_path, mutate):
    fixture_run(tmp_path)
    write_report(tmp_path)
    before = {name: (tmp_path / name).read_bytes() for name in ("REPORT.md", "summary.json", "NOTES.md")}
    bad = row()
    mutate(bad)
    save_rows(tmp_path, [bad])
    with pytest.raises(ValueError):
        write_report(tmp_path)
    assert all((tmp_path / name).read_bytes() == text for name, text in before.items())


def test_duplicate_attempt(tmp_path):
    fixture_run(tmp_path, records=[row(), row()])
    with pytest.raises(ValueError, match="duplicate"):
        write_report(tmp_path)
    assert not (tmp_path / "REPORT.md").exists()


@pytest.mark.parametrize("bad", ['{', '{"model":"a","model":"b"}', 'NaN', '[]'])
def test_corrupt_json_fails_closed(tmp_path, bad):
    fixture_run(tmp_path)
    (tmp_path / "results.jsonl").write_text(bad)
    with pytest.raises(ValueError):
        write_report(tmp_path)
    assert not (tmp_path / "summary.json").exists()


def test_escape_and_only_existing_safe_links(tmp_path):
    model = "m|evil\n[go](https://evil) <script> *bold*"
    manifest = fixture_run(tmp_path, models=[model])
    manifest["participant"] = "<img src=x>|[click](https://evil)\n# heading"
    manifest["endpoint"] = "SECRET_ENDPOINT_TOKEN"
    manifest["model_sources"] = {model: {"model_card_url": "https://safe/card", "license_url": "https://safe/license"}}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    save_rows(tmp_path, [{**row(), "model": model, "raw_response": "model-1/B01-r1.raw.json"}])
    directory = tmp_path / "model-1"
    directory.mkdir()
    (directory / "B01-r1.raw.json").write_text('{"secret":"DO_NOT_DUMP"}')
    (directory / "B01-r1.solution.py").write_text("raise AssertionError('never execute')")
    text = write_report(tmp_path).read_text()
    assert "<script>" not in text and "[go]" not in text and "<img" not in text
    assert "m&#124;evil" in text and "&#91;click&#93;" in text
    assert "DO_NOT_DUMP" not in text and "SECRET_ENDPOINT_TOKEN" not in text
    assert "[raw JSON](model-1/B01-r1.raw.json)" in text
    assert "[solution](model-1/B01-r1.solution.py)" in text
    assert "[pytest log]" not in text
    assert "https://safe/card" in text


def test_symlink_artifact_not_linked(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    fixture_run(root, records=[row()])
    (tmp_path / "secret").write_text("secret")
    (root / "model-1").mkdir()
    (root / "model-1/B01-r1.raw.json").symlink_to(tmp_path / "secret")
    assert "[raw JSON]" not in write_report(root).read_text()


def test_notes_preserved_and_warmup_separate(tmp_path):
    fixture_run(tmp_path, records=[row()])
    (tmp_path / "model-1").mkdir()
    (tmp_path / "model-1/metadata.json").write_text(json.dumps({"warmup": {"status": "ok", "elapsed_seconds": 900}, "show": {"secret": "NO_DUMP"}}))
    text = write_report(tmp_path).read_text()
    assert "900" in text and "NO_DUMP" not in text
    assert summary(tmp_path)["completed"] == 1
    notes = tmp_path / "NOTES.md"
    assert "발견 1" in notes.read_text() and "발견 2" in notes.read_text()
    notes.write_text("human notes\nkeep exactly")
    write_report(tmp_path)
    assert notes.read_text() == "human notes\nkeep exactly"


def test_cloud_five_once(tmp_path):
    manifest = fixture_run(tmp_path)
    manifest.update(command="import-cloud", cases=list(CLOUD_IDS), repeats=1, planned_per_model=5)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    save_rows(tmp_path, [row(case) for case in CLOUD_IDS])
    (tmp_path / "B01-r1.raw.txt").write_text("synthetic")
    text = write_report(tmp_path).read_text()
    assert "5/5" in text and "해당 없음 (1회)" in text
    assert "[raw text](B01-r1.raw.txt)" in text


def test_environment_no_nvidia_no_identity(monkeypatch):
    calls = []
    def missing(args, **kwargs):
        calls.append((args, kwargs))
        raise FileNotFoundError("sensitive /local/path must not appear")
    monkeypatch.setattr("harness.reporting.subprocess.run", missing)
    monkeypatch.setattr("harness.reporting.platform.system", lambda: "Darwin")
    monkeypatch.setattr("harness.reporting.platform.release", lambda: "test-release")
    monkeypatch.setattr("harness.reporting.platform.machine", lambda: "arm64")
    monkeypatch.setattr("harness.reporting.platform.node", lambda: pytest.fail("hostname accessed"))
    result = capture_environment()
    assert result["ram_bytes"] is None and result["ram_unavailable_reason"]
    assert result["nvidia_gpus"] is None and result["nvidia_unavailable_reason"]
    assert "/local/path" not in json.dumps(result)
    assert "hostname" not in result
    assert all(options["timeout"] <= 3 and "shell" not in options for _, options in calls)
    assert calls[-1][0][1] == "--query-gpu=name,memory.total,driver_version"


def test_environment_mocked_gpu(monkeypatch):
    def command(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, "GPU Model, 8192, 555.1\n")
    monkeypatch.setattr("harness.reporting.subprocess.run", command)
    monkeypatch.setattr("harness.reporting.platform.system", lambda: "Other")
    result = capture_environment()
    assert result["nvidia_gpus"] == [{"name": "GPU Model", "memory_total_mib": 8192, "driver_version": "555.1"}]
    assert result["nvidia_unavailable_reason"] is None


def test_two_models_completeness_independent(tmp_path):
    fixture_run(tmp_path, models=["model:1", "model:2"],
                records=[row(case, repeat) for case in CASE_IDS for repeat in (1, 2)])
    text = write_report(tmp_path).read_text()
    data = json.loads((tmp_path / "summary.json").read_text())
    assert data["model:1"]["complete"]
    assert not data["model:2"]["complete"] and data["model:2"]["not_run"] == 20
    assert "전체: 미완료; 누락 20" in text


def test_full_collection_with_infra_still_warns(tmp_path):
    rows = [row(case, repeat) for case in CASE_IDS for repeat in (1, 2)]
    rows[0]["status"] = "evaluator_error"
    fixture_run(tmp_path, records=rows)
    text = write_report(tmp_path).read_text()
    assert summary(tmp_path)["complete"]
    assert not summary(tmp_path)["valid_for_comparison"]
    assert "전체: 완료; 누락 0; 인프라 오류 1" in text


def test_corrupt_metadata_does_not_overwrite(tmp_path):
    fixture_run(tmp_path)
    write_report(tmp_path)
    previous = (tmp_path / "REPORT.md").read_bytes()
    (tmp_path / "model-1").mkdir()
    (tmp_path / "model-1/metadata.json").write_text('{"warmup": []}')
    with pytest.raises(ValueError):
        write_report(tmp_path)
    assert (tmp_path / "REPORT.md").read_bytes() == previous


def test_symlink_output_rejected(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    fixture_run(root)
    outside = tmp_path / "private"
    outside.write_text("unchanged")
    (root / "summary.json").symlink_to(outside)
    with pytest.raises(ValueError):
        write_report(root)
    assert outside.read_text() == "unchanged"
    assert not (root / "REPORT.md").exists()


@pytest.mark.parametrize("bad", ["models", "cases", "repeats", "planned_per_model", "schema_version"])
def test_invalid_manifest_plan(tmp_path, bad):
    manifest = fixture_run(tmp_path)
    manifest[bad] = {"models": ["m", "m"], "cases": ["B01", "B01"], "repeats": True,
                     "planned_per_model": 0, "schema_version": 99}[bad]
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        write_report(tmp_path)
    assert not (tmp_path / "REPORT.md").exists()


def test_environment_timeout(monkeypatch):
    def timeout(args, **kwargs):
        raise subprocess.TimeoutExpired(args, 3)
    monkeypatch.setattr("harness.reporting.subprocess.run", timeout)
    monkeypatch.setattr("harness.reporting.platform.system", lambda: "Other")
    result = capture_environment()
    assert result["nvidia_gpus"] is None and result["nvidia_unavailable_reason"]


@pytest.mark.parametrize("status", ["interrupted", "incomplete", "in_progress"])
def test_manifest_incomplete_overrides_twenty_records(tmp_path, status):
    manifest = fixture_run(tmp_path, records=[row(case, repeat) for case in CASE_IDS for repeat in (1, 2)])
    manifest["run_status"] = status
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    text = write_report(tmp_path).read_text()
    data = summary(tmp_path)
    assert data["not_run"] == 0
    assert not data["complete"] and not data["valid_for_comparison"]
    assert "미완료" in text and status.replace("_", "&#95;") in text
    assert "실행 시 소스 작업 트리가 변경된 상태" in text
