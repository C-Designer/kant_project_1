"""Mocked end-to-end personal workflow; never calls a model or executes a solution."""
import html
import json
from pathlib import Path

from harness import __main__ as cli
from harness.core import write_json, atomic_write


def test_personal_run_report_notes_and_separate_participants(tmp_path, monkeypatch):
    prompts = []
    calls = []
    monkeypatch.setattr(cli, 'capture_environment', lambda: {'python_version': '3.12.test'})
    monkeypatch.setattr(cli, 'source_state', lambda: {'source_commit': 'a' * 40, 'source_dirty': False})
    monkeypatch.setattr(cli, 'python_preflight', lambda: {'backend': 'python-subprocess', 'python_version': '3.12.test', 'pytest_version': '8.test'})

    class FakeOllama:
        def __init__(self, url, timeout):
            pass

        def request(self, route, payload=None, raw_path=None):
            calls.append(route)
            value = {'details': {'quantization_level': 'mock'}} if route == '/api/show' else {'done': True}
            if raw_path:
                write_json(raw_path, value)
            return value, 0.01

        def generate(self, model, prompt, options, raw_path):
            prompts.append(prompt)
            value = {'model': model, 'done': True, 'response': '```python\npass\n```',
                     'eval_count': 10, 'eval_duration': 1000000000, 'load_duration': 0}
            write_json(raw_path, value)
            return value, 2

        def ps(self, model, raw_path):
            value = {'models': [{'model': model, 'size_vram': 1048576}]}
            write_json(raw_path, value)
            return value

    def fake_evaluate(code, directory, **kwargs):
        atomic_write(kwargs['log_path'], 'Synthetic pytest output. No solution was executed.\n')
        return {'status': 'solved', 'evaluation_elapsed_seconds': 0.01}

    monkeypatch.setattr(cli, 'Ollama', FakeOllama)
    monkeypatch.setattr(cli, 'evaluate', fake_evaluate)
    case_root = Path(__file__).resolve().parents[1] / 'cases'
    for participant in ('alice', 'bob'):
        result = cli.main(['run-model', '--participant', participant, '--model', 'synthetic:1',
                           '--results-root', str(tmp_path / 'results'), '--run-id', 'run-a',
                           '--cases', str(case_root), '--device-label', 'shared-test-pc'])
        assert result == 0
        run = tmp_path / 'results' / participant / 'run-a'
        manifest = json.loads((run / 'manifest.json').read_text())
        assert manifest['participant'] == participant and manifest['models'] == ['synthetic:1']
        assert manifest['planned_attempts'] == 20 and manifest['completed_attempts'] == 20
        assert manifest['run_status'] == 'completed'
        summary = json.loads((run / 'summary.json').read_text())['synthetic:1']
        assert summary['solved'] == 20 and summary['complete']
        report = (run / 'REPORT.md').read_text()
        assert 'Python evaluator backend: python-subprocess' in html.unescape(report)
        assert 'current user with filesystem and network access' in report
        assert '20/20' in report and 'model-1/B01-r1.raw.json' in report
        assert 'model-1/B10-r2.pytest.log' in report
        (run / 'NOTES.md').write_text('Human interpretation must survive regeneration.\n')
        assert cli.main(['report', str(run)]) == 0
        assert (run / 'NOTES.md').read_text() == 'Human interpretation must survive regeneration.\n'
    assert len(prompts) == 42  # two independent personal runs, each warmup1 + attempts20
    assert all('=== test_hidden.py ===' not in p and '=== reference.py ===' not in p for p in prompts)
    assert calls.count('/api/show') == 2 and calls.count('/api/generate') == 2  # unload only
