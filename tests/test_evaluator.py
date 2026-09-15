"""Only authored benign solutions are executed by these evaluator tests."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
from harness import evaluator
from harness.evaluator import PREFIX, evaluate, parse_report, python_preflight


def is_runner_command(command):
    """Windows _kill_tree spawns taskkill.exe through the same patched Popen."""
    return command[0] == sys.executable


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


@pytest.mark.parametrize('mutation', ['duplicate', 'unexpected_file', 'bad_outcome', 'bad_errors'])
def test_report_integrity(mutation):
    data = json.loads(report()[len(PREFIX):])
    if mutation == 'duplicate':
        data['tests'].append(data['tests'][0])
    elif mutation == 'unexpected_file':
        data['tests'][0]['nodeid'] = 'other.py::test_one'
    elif mutation == 'bad_outcome':
        data['tests'][0]['outcome'] = 'unknown'
    else:
        data['collection_errors'] = [123]
    with pytest.raises(ValueError):
        parse_report(PREFIX + json.dumps(data), 0)


@pytest.fixture
def small_case(tmp_path):
    for filename, arg, expected in [('test_public.py', 2, 3), ('test_hidden.py', -4, -3)]:
        (tmp_path / filename).write_text(
            f'from solution import increment\ndef test_increment(): assert increment({arg}) == {expected}\n', encoding='utf-8')
    return tmp_path


def test_actual_solution_pass_and_failure(small_case):
    good = evaluate('def increment(x): return x + 1\n', small_case)
    bad = evaluate('def increment(x): return x - 1\n', small_case)
    assert good['status'] == 'solved', good
    assert good['process_exit_code'] == 0
    assert good['groups']['public']['passed'] == good['groups']['hidden']['passed'] == 1
    assert good['test_count'] == 2
    assert good['collection_errors'] == []
    assert good['evaluation_elapsed_seconds'] > 0
    assert bad['status'] == 'test_failure', bad
    assert bad['process_exit_code'] == 1
    assert bad['groups']['public']['failed'] == bad['groups']['hidden']['failed'] == 1


def test_collection_error(small_case):
    result = evaluate('raise ValueError("authored collection error")\n', small_case)
    assert result['status'] == 'test_failure'
    assert len(result['collection_errors']) == 2
    assert not result['all_pass']


def test_preflight_real():
    metadata = python_preflight()
    assert metadata['backend'] == 'python-subprocess'
    assert metadata['python_version'].startswith('3.12.')
    assert metadata['pytest_version']
    assert len(metadata['runner_sha256']) == 64
    assert str(Path.home()) not in json.dumps(metadata)
    assert sys.executable not in json.dumps(metadata)


def test_preflight_uses_current_interpreter(monkeypatch):
    def run(command, **kwargs):
        assert command[:3] == [sys.executable, '-I', '-c']
        assert 'pytest' in command[-1]
        assert kwargs['timeout'] == 15
        assert kwargs['env']['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] == '1'
        assert not kwargs.get('shell', False)
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            'python_version': '3.12.9', 'pytest_version': '8.3.5'}))
    monkeypatch.setattr(evaluator.subprocess, 'run', run)
    assert python_preflight()['python_version'] == '3.12.9'


@pytest.mark.parametrize('failure', ['missing_pytest', 'missing_python', 'timeout', 'invalid'])
def test_preflight_failure(monkeypatch, failure):
    def run(*args, **kwargs):
        if failure == 'missing_python':
            raise FileNotFoundError('private path')
        if failure == 'timeout':
            raise subprocess.TimeoutExpired('python', 15)
        if failure == 'invalid':
            return SimpleNamespace(returncode=0, stdout='{}')
        return SimpleNamespace(returncode=1, stdout='', stderr='No module named pytest')
    monkeypatch.setattr(evaluator.subprocess, 'run', run)
    with pytest.raises(ValueError, match='Python preflight failed'):
        python_preflight()


def test_command_environment_and_only_copied_inputs(monkeypatch, small_case):
    for name in ('OPENAI_API_KEY', 'AWS_SECRET_ACCESS_KEY', 'PYTHONPATH', 'PYTEST_ADDOPTS',
                 'PYTEST_PLUGINS', 'HTTP_PROXY', 'HOME', 'PATH'):
        monkeypatch.setenv(name, 'must-not-leak')
    (small_case / 'conftest.py').write_text('raise RuntimeError("must not be copied")', encoding='utf-8')
    (small_case / 'reference.py').write_text('raise RuntimeError("must not be copied")', encoding='utf-8')
    actual = evaluator.subprocess.Popen
    workdirs = []
    def popen(command, **kwargs):
        if not is_runner_command(command):
            return actual(command, **kwargs)
        assert command == [sys.executable, '-I', '-B', str(evaluator.RUNNER)]
        assert not kwargs.get('shell', False)
        env = kwargs['env']
        assert 'must-not-leak' not in env.values()
        assert env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] == '1'
        assert kwargs['stdin'] == subprocess.DEVNULL
        if os.name == 'posix':
            assert kwargs['start_new_session'] is True
        work = Path(kwargs['cwd'])
        workdirs.append(work)
        assert {p.name for p in work.iterdir()} == {'solution.py', 'test_public.py', 'test_hidden.py'}
        return actual(command, **kwargs)
    monkeypatch.setattr(evaluator.subprocess, 'Popen', popen)
    result = evaluate('def increment(x): return x + 1\n', small_case)
    assert result['status'] == 'solved', result
    assert all(not work.exists() for work in workdirs)


@pytest.mark.parametrize('timeout', [0, -1, float('inf'), float('nan'), True])
def test_invalid_timeout(small_case, timeout):
    assert evaluate('pass', small_case, wall_timeout=timeout)['status'] == 'evaluator_error'


def test_actual_timeout_captured_and_cleaned(monkeypatch, small_case):
    actual = evaluator.subprocess.Popen
    workdirs = []
    def popen(command, **kwargs):
        if is_runner_command(command):
            workdirs.append(Path(kwargs['cwd']))
        return actual(command, **kwargs)
    monkeypatch.setattr(evaluator.subprocess, 'Popen', popen)
    log = small_case / 'timeout.log'
    started = time.monotonic()
    result = evaluate('import os,time\nos.write(1,b"authored timeout marker\\n")\ntime.sleep(30)\n',
                      small_case, wall_timeout=0.8, log_path=log)
    assert result['status'] == 'timeout', result
    assert result['process_exit_code'] is not None
    assert time.monotonic() - started < 5
    assert 'authored timeout marker' in log.read_text(encoding='utf-8')
    assert all(not work.exists() for work in workdirs)


@pytest.mark.skipif(os.name != 'posix', reason='POSIX process group runtime validation')
@pytest.mark.parametrize('timeout', [True, False])
def test_child_process_cleanup(small_case, timeout):
    # Benign delayed marker proves the child did not survive either parent outcome.
    marker = small_case / 'child-survived'
    child = f'import time,pathlib; time.sleep(1.5); pathlib.Path({str(marker)!r}).touch()'
    code = ('import subprocess,sys,time\n'
            f'subprocess.Popen([sys.executable,"-I","-c",{child!r}])\n'
            + ('time.sleep(30)\n' if timeout else '')
            + 'def increment(x): return x+1\n')
    result = evaluate(code, small_case, wall_timeout=0.7 if timeout else 5)
    assert result['status'] == ('timeout' if timeout else 'solved'), result
    time.sleep(1.6)
    assert not marker.exists()


def test_output_is_bounded(small_case):
    log = small_case / 'output.log'
    result = evaluate('import os\nos.write(1,b"x"*3000000)\ndef increment(x): return x+1\n',
                      small_case, log_path=log)
    assert result['status'] == 'solved', result
    assert log.stat().st_size <= evaluator.OUTPUT_LIMIT
    assert log.read_text(encoding='utf-8').rstrip().splitlines()[-1].startswith(PREFIX)


def test_launch_failure_is_evaluator_error(monkeypatch, small_case):
    def missing(*args, **kwargs):
        raise FileNotFoundError('private location')
    monkeypatch.setattr(evaluator.subprocess, 'Popen', missing)
    result = evaluate('pass', small_case)
    assert result['status'] == 'evaluator_error'
    assert 'private location' not in json.dumps(result)
