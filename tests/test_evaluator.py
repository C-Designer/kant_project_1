import json
import subprocess
from types import SimpleNamespace
import pytest
from harness.evaluator import PREFIX, docker_command, evaluate, parse_report


def report(exit_code=0, public='passed', hidden='passed'):
    return PREFIX + json.dumps({'version': 1, 'exit_code': exit_code, 'collection_errors': [],
        'tests': [{'nodeid': 'test_public.py::test_one', 'outcome': public},
                  {'nodeid': 'test_hidden.py::test_two', 'outcome': hidden}]})


def test_parser():
    assert parse_report('ordinary captured output\n' + report(), 0)['all_pass']
    parsed = parse_report(report(1, hidden='failed'), 1)
    assert parsed['groups']['hidden']['failed'] == 1
    assert not parsed['all_pass']
    assert not parse_report(report(0, hidden='skipped'), 0)['all_pass']


@pytest.mark.parametrize('text,code', [('{}', 0), (report(), 1), (report() + '\nextra output', 0),
                                       (PREFIX + '{}', 0), (PREFIX + 'null', 0)])
def test_bad_report(text, code):
    with pytest.raises((ValueError, TypeError)):
        parse_report(text, code)


def test_isolation_flags():
    command = docker_command('known-name', '/tmp/input', 'kant-harness:1')
    for token in ['--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt',
                  'no-new-privileges', '--pids-limit', '--memory', '--memory-swap', '--cpus',
                  '--user', '65532:65532', '--tmpfs', '--rm']:
        assert token in command
    assert 'type=bind,src=/tmp/input,dst=/work,readonly' in command
    assert not any('docker.sock' in x for x in command)
    assert command[-2:] == ['-I', '/opt/harness/docker_runner.py']


def test_timeout_cleans_known_container(monkeypatch, tmp_path):
    for name in ['test_public.py', 'test_hidden.py']:
        (tmp_path / name).write_text('def test_one(): assert True\n')
    commands = []
    def fake_run(command, **kwargs):
        commands.append(command)
        if command[1] == 'run':
            mount = command[command.index('--mount') + 1]
            assert 'readonly' in mount
            raise subprocess.TimeoutExpired(command, 1)
        return SimpleNamespace(returncode=0, stdout=b'')
    monkeypatch.setattr('harness.evaluator.subprocess.run', fake_run)
    monkeypatch.setattr('harness.evaluator.run_bounded', lambda command, capture, timeout: fake_run(command))
    result = evaluate('raise RuntimeError("must not run on host")', tmp_path, wall_timeout=1)
    assert result['status'] == 'timeout'
    assert commands[-1] == ['docker', 'rm', '-f', result['container']]


def test_docker_missing(monkeypatch, tmp_path):
    for name in ['test_public.py', 'test_hidden.py']:
        (tmp_path / name).write_text('')
    def missing(*args, **kwargs):
        raise FileNotFoundError('docker not available')
    monkeypatch.setattr('harness.evaluator.subprocess.run', missing)
    monkeypatch.setattr('harness.evaluator.run_bounded', missing)
    assert evaluate('pass', tmp_path)['status'] == 'docker_error'


def test_preflight_checks_daemon_and_image(monkeypatch):
    from harness.evaluator import docker_preflight
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        assert kwargs['timeout'] == 15
        return SimpleNamespace(returncode=0, stdout='27.5.1\n' if command[1] == 'version'
                               else 'sha256:' + 'b' * 64 + '\n', stderr='')
    monkeypatch.setattr('harness.evaluator.subprocess.run', run)
    metadata = docker_preflight('custom:1')
    assert metadata == {'docker_server_version': '27.5.1', 'image_id': 'sha256:' + 'b' * 64,
                        'requested_image': 'custom:1'}
    assert calls == [['docker', 'version', '--format', '{{.Server.Version}}'],
                     ['docker', 'image', 'inspect', '--format', '{{.Id}}', 'custom:1']]


@pytest.mark.parametrize('version,image_id', [('', 'sha256:' + 'a' * 64),
                                             ('<no value>', 'sha256:' + 'a' * 64),
                                             ('27.5.1', ''), ('27.5.1', 'not-an-image-id')])
def test_preflight_rejects_invalid_metadata(monkeypatch, version, image_id):
    from harness.evaluator import docker_preflight
    def run(command, **kwargs):
        return SimpleNamespace(returncode=0, stdout=version if command[1] == 'version' else image_id,
                               stderr='')
    monkeypatch.setattr('harness.evaluator.subprocess.run', run)
    with pytest.raises(ValueError, match='Docker preflight failed'):
        docker_preflight('custom:1')
