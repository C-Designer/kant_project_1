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
    monkeypatch.setattr('harness.__main__.capture_environment', lambda: {'os': 'test-os'})
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
    monkeypatch.setattr('harness.__main__.capture_environment', lambda: {'os': 'test-os'})
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


@pytest.fixture
def local_mocks(monkeypatch):
    import harness.__main__ as cli
    state = {'generate': [], 'requests': [], 'reports': [], 'evaluations': []}
    monkeypatch.setattr(cli, 'capture_environment', lambda: {'os': 'test-os'})
    monkeypatch.setattr(cli, 'source_state', lambda: {'source_commit': 'a' * 40, 'source_dirty': True})
    monkeypatch.setattr(cli, 'docker_preflight', lambda image: {'image_id': 'sha256:fixed'})
    def report(out):
        assert (out / 'summary.json').exists()
        state['reports'].append(out)
        return out / 'report.md'
    monkeypatch.setattr(cli, 'write_report', report)
    class FakeOllama:
        def __init__(self, *args):
            pass
        def request(self, endpoint, body, out):
            state['requests'].append((endpoint, body))
            return {}, .01
        def generate(self, model, prompt, options, out):
            state['generate'].append((model, prompt, dict(options)))
            if len(state['generate']) == state.get('fail_at'):
                raise state.get('failure', KeyboardInterrupt)()
            return {'response': '```python\npass\n```', 'done': True}, .01
        def ps(self, *args):
            return {'models': []}
    def evaluate(*args, **kwargs):
        state['evaluations'].append(kwargs)
        return {'status': 'solved'}
    monkeypatch.setattr(cli, 'Ollama', FakeOllama)
    monkeypatch.setattr(cli, 'evaluate', evaluate)
    return state


def individual_args(tmp_path):
    cases = tmp_path / 'cases'
    make_cases(cases)
    return ['run-model', '--participant', 'student-1', '--model', 'one:7b',
            '--cases', str(cases), '--results-root', str(tmp_path / 'results')]


def test_individual_twenty_warmup_unload_metadata(tmp_path, local_mocks):
    args = individual_args(tmp_path) + ['--run-id', 'experiment_1', '--device-label', 'My device',
                                      '--model-card-url', 'https://example.com/card',
                                      '--license-url', 'https://example.com/license']
    assert main(args) == 0
    out = tmp_path / 'results/student-1/experiment_1'
    manifest = json.loads((out / 'manifest.json').read_text())
    assert manifest['participant'] == 'student-1'
    assert manifest['device_label'] == 'My device'
    assert manifest['model_card_url'] == 'https://example.com/card'
    assert manifest['license_url'] == 'https://example.com/license'
    assert 'user supplied' in manifest['metadata_provenance']
    assert manifest['environment'] == {'os': 'test-os'}
    assert manifest['source_commit'] == 'a' * 40 and manifest['source_dirty'] is True
    assert manifest['completed_attempts'] == manifest['planned_attempts'] == 20
    assert manifest['run_status'] == 'completed'
    assert len(local_mocks['generate']) == 21
    assert local_mocks['generate'][0][1] == 'Reply with OK.'
    assert [call[2]['seed'] for call in local_mocks['generate'][1:]] == [42, 43] * 10
    assert len(local_mocks['evaluations']) == 20
    assert all(e['image'] == 'sha256:fixed' for e in local_mocks['evaluations'])
    assert local_mocks['requests'][-1] == ('/api/generate', {'model': 'one:7b', 'stream': False, 'keep_alive': 0})
    assert local_mocks['reports'] == [out]
    assert len((out / 'results.jsonl').read_text().splitlines()) == 20
    assert main(args) == 2
    assert len(local_mocks['generate']) == 21  # collision never starts a generation


def test_individual_automatic_new_paths(tmp_path, local_mocks):
    import re
    args = individual_args(tmp_path)
    assert main(args) == main(args) == 0
    outputs = list((tmp_path / 'results/student-1').iterdir())
    assert len(outputs) == 2
    assert all(re.fullmatch(r'\d{8}t\d{6}z-[0-9a-f]{8}', p.name) for p in outputs)


@pytest.mark.parametrize('value', ['../x', '.', '..', 'a/b', 'a\\b', 'a.b', '-x', '_x', '',
                                   'a' * 65, 'é', 'CON', 'con', 'prn', 'aux', 'nul',
                                   'com1', 'com9', 'lpt1', 'lpt9', 'CoM2', 'UPPER'])
@pytest.mark.parametrize('flag', ['--participant', '--run-id'])
def test_individual_rejects_unsafe_identifiers(value, flag):
    args = ['run-model', '--participant', 'student', '--model', 'one:7b']
    with pytest.raises(SystemExit):
        parser().parse_args(args + [flag, value])


def test_individual_options_and_old_participant_rejected():
    args = parser().parse_args(['run-model', '--participant', 'a', '--model', 'one:7b'])
    assert str(args.results_root) == 'results' and args.out is None
    assert args.num_ctx == 8192 and args.num_predict == 2048
    assert args.temperature == .2 and args.seed == 42
    with pytest.raises(SystemExit):
        parser().parse_args(['run', '--models', 'one:7b', 'two:7b', '--out', 'out', '--participant', 'a'])
    with pytest.raises(SystemExit):
        parser().parse_args(['run-model', '--participant', 'a', '--model', 'one'])


def test_individual_no_docker_no_model_calls(tmp_path, local_mocks, monkeypatch):
    def blocked(*args):
        raise ValueError('Docker preflight failed')
    def forbidden(*args):
        pytest.fail('must not construct model client')
    monkeypatch.setattr('harness.__main__.docker_preflight', blocked)
    monkeypatch.setattr('harness.__main__.Ollama', forbidden)
    assert main(individual_args(tmp_path)) == 2
    assert not (tmp_path / 'results').exists()
    assert not local_mocks['generate'] and not local_mocks['reports']


@pytest.mark.parametrize('failure,code,status', [(KeyboardInterrupt, 130, 'interrupted'),
                                               (RuntimeError, 2, 'incomplete')])
def test_partial_run_reports_only_completed(tmp_path, local_mocks, failure, code, status):
    local_mocks.update(fail_at=4, failure=failure)
    assert main(individual_args(tmp_path) + ['--run-id', 'partial']) == code
    out = tmp_path / 'results/student-1/partial'
    manifest = json.loads((out / 'manifest.json').read_text())
    summary = json.loads((out / 'summary.json').read_text())['one:7b']
    assert manifest['run_status'] == status
    assert manifest['completed_attempts'] == summary['completed'] == 2
    assert summary['planned'] == 20
    assert local_mocks['reports'] == [out]
    assert local_mocks['requests'][-1][1]['keep_alive'] == 0


def test_report_command_no_model_or_docker(tmp_path, monkeypatch):
    import harness.__main__ as cli
    calls = []
    def forbidden(*args):
        pytest.fail('report must not inspect Docker/models/environment')
    monkeypatch.setattr(cli, 'docker_preflight', forbidden)
    monkeypatch.setattr(cli, 'Ollama', forbidden)
    monkeypatch.setattr(cli, 'capture_environment', forbidden)
    monkeypatch.setattr(cli, 'write_report', lambda out: calls.append(out) or out / 'report.md')
    assert main(['report', str(tmp_path)]) == 0
    assert calls == [tmp_path]


def test_legacy_two_models_counts(tmp_path, local_mocks):
    cases = tmp_path / 'cases'
    make_cases(cases)
    out = tmp_path / 'legacy'
    assert main(['run', '--models', 'one:7b', 'two:7b', '--cases', str(cases), '--out', str(out)]) == 0
    assert len(local_mocks['generate']) == 42
    assert len(local_mocks['evaluations']) == 40
    unloads = [body for endpoint, body in local_mocks['requests'] if body.get('keep_alive') == 0]
    assert [body['model'] for body in unloads] == ['one:7b', 'two:7b']
    assert local_mocks['reports'] == [out]


def test_git_provenance_read_only_and_private(monkeypatch):
    from harness.__main__ import source_state
    commands = []
    class Process:
        returncode = 0
        def __init__(self, command, **kwargs):
            self.command = command
            commands.append(command)
        def communicate(self, timeout):
            return (b'a' * 40 if 'rev-parse' in self.command else b' M secret-user-path\n'), None
    monkeypatch.setattr('harness.__main__.subprocess.Popen', Process)
    assert source_state() == {'source_commit': 'a' * 40, 'source_dirty': True}
    assert commands[0][3:] == ['rev-parse', 'HEAD']
    assert commands[1][3:] == ['status', '--porcelain', '--untracked-files=normal', '--', '.',
                               ':(exclude)results', ':(exclude)runs']


def test_git_unavailable_is_unknown(monkeypatch):
    from harness.__main__ import source_state
    def unavailable(*args, **kwargs):
        raise FileNotFoundError('sensitive path must not be reported')
    monkeypatch.setattr('harness.__main__.subprocess.Popen', unavailable)
    assert source_state() == {'source_commit': None, 'source_dirty': None}


def test_individual_real_report_metadata(tmp_path, local_mocks, monkeypatch):
    from harness.reporting import write_report
    monkeypatch.setattr('harness.__main__.write_report', write_report)
    assert main(individual_args(tmp_path) + ['--run-id', 'report-integration',
                '--model-card-url', 'https://example.com/model-card',
                '--license-url', 'https://example.com/license']) == 0
    out = tmp_path / 'results/student-1/report-integration'
    import html
    report = html.unescape((out / 'REPORT.md').read_text())
    assert 'https://example.com/model-card' in report
    assert 'https://example.com/license' in report
    assert (out / 'NOTES.md').exists()
