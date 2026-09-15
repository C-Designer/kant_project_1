import json
import pytest
from harness.__main__ import main, parser
from harness.core import CASE_IDS, CLOUD_IDS


def test_defaults():
    args = parser().parse_args(['run', '--models', 'one:7b', 'two:7b', '--out', 'output'])
    assert args.num_ctx == 8192 and args.num_predict == 2048
    assert args.seed == 42 and args.temperature == .2
    assert parser().parse_args(['export-cloud', '--out', 'out']).repeats == 1
    assert CLOUD_IDS == ('B01', 'B04', 'B06', 'B08', 'B10')


@pytest.mark.parametrize('extra', [['--num-ctx', '0'], ['--num-predict', '-1'], ['--cpus', 'nan'],
                                  ['--wall-timeout', '0'], ['--temperature', '-.1'],
                                  ['--memory', '0m'], ['--pids', '-1'], ['--temperature', 'inf']])
def test_invalid_args(extra):
    with pytest.raises(SystemExit):
        parser().parse_args(['run', '--models', 'one:7b', 'two:7b', '--out', 'out'] + extra)


def test_full_tags_required():
    with pytest.raises(SystemExit):
        parser().parse_args(['run', '--models', 'one', 'two', '--out', 'out'])


def make_cases(root):
    for case in CASE_IDS:
        directory = root / case
        directory.mkdir(parents=True)
        for filename in ('prompt.md', 'starter.py', 'test_public.py'):
            (directory / filename).write_text('visible ' + filename)
        (directory / 'reference.py').write_text('REFERENCE_SECRET')
        (directory / 'test_hidden.py').write_text('HIDDEN_SECRET')


def test_cloud_export_import_missing(tmp_path):
    cases, bundle, output, responses = [tmp_path / n for n in ('cases', 'bundle', 'run', 'responses')]
    make_cases(cases)
    responses.mkdir()
    assert main(['export-cloud', '--cases', str(cases), '--out', str(bundle)]) == 0
    assert len((bundle / 'requests.jsonl').read_text().splitlines()) == 5
    assert not any('HIDDEN_SECRET' in p.read_text() or 'REFERENCE_SECRET' in p.read_text()
                   for p in bundle.iterdir())
    assert main(['import-cloud', '--cases', str(cases), '--bundle', str(bundle), '--responses',
                 str(responses), '--model', 'provider/model', '--out', str(output)]) == 0
    summary = json.loads((output / 'summary.json').read_text())['provider/model']
    assert summary['planned'] == summary['completed'] == 5
    assert summary['statuses'] == {'missing_response': 5}
    assert summary['solved'] == 0
    assert main(['summarize', str(output)]) == 0


def test_extract_cli_never_executes(tmp_path):
    source, dest = tmp_path / 'raw.txt', tmp_path / 'solution.py'
    source.write_text('```python\nraise RuntimeError("not executed")\n```')
    assert main(['extract', str(source), '--out', str(dest)]) == 0
    assert dest.read_text().startswith('raise RuntimeError')
    assert main(['extract', str(source), '--out', str(dest)]) == 2


@pytest.mark.parametrize('repeats', ['0', '2', '-1'])
def test_cloud_export_rejects_other_repeat_counts(repeats):
    with pytest.raises(SystemExit):
        parser().parse_args(['export-cloud', '--out', 'out', '--repeats', repeats])


@pytest.mark.parametrize('repeats', [0, 2, -1, None, True, 1.0, '1'])
def test_cloud_import_rejects_other_repeat_counts(tmp_path, repeats, capsys):
    bundle = tmp_path / 'bundle'
    bundle.mkdir()
    (bundle / 'bundle.json').write_text(json.dumps({
        'schema_version': 1, 'cases': list(CLOUD_IDS), 'repeats': repeats}))
    output = tmp_path / 'run'
    assert main(['import-cloud', '--bundle', str(bundle), '--responses', str(tmp_path / 'responses'),
                 '--model', 'cloud/version', '--out', str(output)]) == 2
    assert 'exactly one repeat' in capsys.readouterr().err
    assert not output.exists()


@pytest.mark.parametrize('failure', ['missing_cli', 'daemon_down', 'missing_image', 'timeout'])
def test_run_preflight_failure_makes_no_ollama_calls(monkeypatch, tmp_path, capsys, failure):
    import subprocess
    from types import SimpleNamespace
    commands = []
    def docker(command, **kwargs):
        commands.append(command)
        if failure == 'missing_cli':
            raise FileNotFoundError('docker')
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(command, 15)
        if failure == 'daemon_down' or command[1] == 'image':
            return SimpleNamespace(returncode=1, stdout='', stderr='unavailable')
        return SimpleNamespace(returncode=0, stdout='27.5.1\n', stderr='')
    def forbidden_client(*args, **kwargs):
        pytest.fail('Ollama must not even be constructed before preflight succeeds')
    monkeypatch.setattr('harness.evaluator.subprocess.run', docker)
    monkeypatch.setattr('harness.__main__.Ollama', forbidden_client)
    output = tmp_path / 'run'
    assert main(['run', '--models', 'a:1', 'b:1', '--out', str(output)]) == 2
    assert 'Docker preflight failed' in capsys.readouterr().err
    assert not output.exists()
    assert len(commands) == (2 if failure == 'missing_image' else 1)


def test_run_records_preflight_metadata_and_pins_image(monkeypatch, tmp_path):
    from types import SimpleNamespace
    image_id = 'sha256:' + 'a' * 64
    events = []
    def docker(command, **kwargs):
        events.append(command[1])
        return SimpleNamespace(returncode=0,
                               stdout='27.5.1\n' if command[1] == 'version' else image_id + '\n',
                               stderr='')
    class FakeOllama:
        def __init__(self, *args):
            assert events == ['version', 'image']
            events.append('ollama')
        def request(self, *args, **kwargs):
            return {}, .01
        def generate(self, *args, **kwargs):
            return {'response': '```python\npass\n```', 'done': True}, .01
        def ps(self, *args, **kwargs):
            return {'models': []}
    evaluated_images = []
    def evaluator(*args, **kwargs):
        evaluated_images.append(kwargs['image'])
        return {'status': 'solved'}
    monkeypatch.setattr('harness.evaluator.subprocess.run', docker)
    monkeypatch.setattr('harness.__main__.Ollama', FakeOllama)
    monkeypatch.setattr('harness.__main__.evaluate', evaluator)
    cases, output = tmp_path / 'cases', tmp_path / 'run'
    make_cases(cases)
    assert main(['run', '--models', 'a:1', 'b:1', '--cases', str(cases), '--out', str(output)]) == 0
    manifest = json.loads((output / 'manifest.json').read_text())
    assert manifest['evaluator']['image_id'] == image_id
    assert manifest['evaluator']['docker_server_version'] == '27.5.1'
    assert manifest['evaluator']['requested_image'] == 'kant-harness:1'
    assert evaluated_images == [image_id] * 40
