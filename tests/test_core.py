import json
import pytest
from harness.core import (CASE_IDS, CLOUD_IDS, ExtractionError, atomic_write, build_prompt,
                          extract_python, metrics, summarize)


@pytest.mark.parametrize('text', ['```python\nprint(1)\n```', '\n```python\nprint(1)\n```\n',
    '```py\n1\n```', '~~~python\n1\n~~~', 'Here:\n```python\n1\n```', '```python\n1\n```\nDone.'])
def test_extract_ignores_surrounding_prose_and_common_labels(text):
    assert extract_python(text) in ('print(1)\n', '1\n')


@pytest.mark.parametrize('text', ['', 'print(1)', '```python\n\n```',
    '```python\n1\n```\n```python\n2\n```', '````python\n1\n````',
    '```python\n1', '```python extra\n1\n```', None])
def test_extraction_rejects(text):
    with pytest.raises(ExtractionError):
        extract_python(text)


def test_no_execution(tmp_path):
    target = tmp_path / 'not-created'
    source = "import pathlib\npathlib.Path(%r).touch()\n" % str(target)
    assert extract_python('```python\n' + source + '```') == source
    assert not target.exists()


def test_prompt_has_no_private_inputs(tmp_path):
    directory = tmp_path / 'B01'
    directory.mkdir()
    for name in ('prompt.md', 'starter.py', 'test_public.py'):
        (directory / name).write_text(name + ' visible', encoding='utf-8')
    # Missing private files must not prevent building a prompt.
    text = build_prompt(tmp_path, 'B01')
    assert 'test_public.py visible' in text
    assert 'reference.py' not in text and 'test_hidden.py' not in text
    with pytest.raises(ValueError):
        build_prompt(tmp_path, '../other')


@pytest.mark.parametrize('value', [None, 0, -1, True, '4', float('nan'), float('inf')])
def test_bad_token_duration(value):
    assert metrics({'eval_count': 10, 'eval_duration': value})['tokens_per_second'] is None
    assert metrics({'eval_count': value, 'eval_duration': 10})['tokens_per_second'] is None


def test_metrics_match_exact_tag():
    result = metrics({'eval_count': 20, 'eval_duration': 2_000_000_000, 'load_duration': 500_000_000},
                     4, {'models': [{'name': 'm:other', 'size_vram': 100},
                                    {'model': 'm:full', 'size_vram': 1048576}]}, 'm:full')
    assert result['tokens_per_second'] == 10
    assert result['vram_mib'] == 1
    assert result['load_duration_seconds'] == .5
    assert metrics({}, ps={'models': [{'name': 'm:other'}]}, model='m:full')['vram_mib'] is None


def test_summary_denominators_include_failure():
    rows = [{'phase': 'attempt', 'model': 'm', 'case': 'B01', 'repeat': 1, 'status': 'solved'},
            {'phase': 'attempt', 'model': 'm', 'case': 'B01', 'repeat': 2, 'status': 'call_transport_error'},
            {'phase': 'warmup', 'model': 'm', 'status': 'solved'}]
    item = summarize(rows, ['m'])['m']
    assert item['planned'] == item['solved_denominator'] == 20
    assert item['n'] == item['completed'] == 2
    assert item['all_repeats_solved_cases'] == 0
    assert item['case_denominator'] == 10
    assert item['call_failures'] == 1
    assert item['mean_tokens_per_second'] is None
    assert summarize([], ['m'])['m']['planned'] == 20
    with pytest.raises(ValueError, match='duplicate'):
        summarize(rows + rows[:1], ['m'])


def test_atomic_write(tmp_path):
    dest = tmp_path / 'nested' / 'raw.json'
    atomic_write(dest, '{"x":1}')
    atomic_write(dest, '{"x":2}')
    assert json.loads(dest.read_text(encoding='utf-8')) == {'x': 2}
    assert list(dest.parent.iterdir()) == [dest]


def test_summary_success_metrics_and_missing():
    rows = [
        {"phase": "attempt", "model": "m", "case": "B01", "repeat": 1, "status": "solved", "metrics": {"elapsed_seconds": 2, "load_duration_seconds": 0, "vram_mib": 0, "tokens_per_second": 10}},
        {"phase": "attempt", "model": "m", "case": "B01", "repeat": 2, "status": "call_transport_error", "metrics": {"elapsed_seconds": 100}},
        {"phase": "attempt", "model": "m", "case": "B02", "repeat": 1, "status": "extraction_failure", "metrics": {"elapsed_seconds": 4}},
    ]
    result = summarize(rows, ["m"])["m"]
    assert result["call_successes"] == 2
    assert result["call_attempts"] == 3
    assert result["not_run"] == 17
    assert result["mean_metrics"]["elapsed_seconds"] == {"mean": 3, "n": 2}
    assert result["mean_metrics"]["load_duration_seconds"] == {"mean": 0, "n": 1}
    assert result["mean_metrics"]["vram_mib"] == {"mean": 0, "n": 1}
    assert result["per_case"]["B02"] == ["extraction_failure", "not_run"]
