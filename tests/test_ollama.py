import json
import pytest
from harness.ollama import CallFailure, Ollama


@pytest.mark.parametrize('url', ['https://user:secret@localhost', 'http://localhost?token=x',
                                  'file:///tmp/server', 'http://localhost/api'])
def test_url_rejects_credentials(url):
    with pytest.raises(ValueError):
        Ollama(url)


def test_generate_independent_options(monkeypatch, tmp_path):
    client = Ollama()
    calls = []
    def request(route, payload, raw_path):
        calls.append(payload)
        return {'response': '```python\npass\n```', 'done': True}, 1.0
    monkeypatch.setattr(client, 'request', request)
    options = {'num_ctx': 4096, 'num_predict': 128, 'temperature': .2, 'seed': 42}
    for _ in range(2):
        client.generate('m:full', 'prompt', options, tmp_path / 'raw')
    assert calls[0] == calls[1]
    assert calls[0]['options'] == options
    assert 'context' not in calls[0] and 'messages' not in calls[0]
    assert calls[0]['stream'] is False


def test_raw_saved_before_json_validation(monkeypatch, tmp_path):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'not json'
    monkeypatch.setattr('harness.ollama.urlopen', lambda *a, **kw: Response())
    target = tmp_path / 'raw.json'
    with pytest.raises(CallFailure) as exc:
        Ollama().request('/api/generate', {}, target)
    assert exc.value.status == 'call_invalid_json'
    assert target.read_bytes() == b'not json'
