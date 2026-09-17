# 실행 결과 (자동 생성)

수치는 자동 계산입니다. 해석은 [NOTES.md](NOTES.md)에 사람이 작성해야 하며 이 보고서는 해석 완료를 주장하지 않습니다.

서로 다른 PC 간 속도 비교는 의미가 없습니다. 공식 두 모델 동일 PC 비교와 클라우드 5×1 실험은 별도 팀 의무입니다.
결과는 results/<participant>/<run-id> 아래 Git 추적 대상으로 보관합니다. 원문 공개 전 키·개인정보를 확인하세요.

## 실행 정보

Execution warning: Generated code runs as the current user with filesystem and network access. A temporary directory, Python -I, and a subprocess wall-time limit are not security isolation. No RAM, CPU, network, or filesystem isolation is provided. Hidden tests and runner output are not protected against adversarial code.
- participant: cloud
- created_utc: 2026&#45;09&#45;16T06:48:44&#46;281565&#43;00:00
- source_commit: d339b0c41dbf1c9580a807f82ee4066dc58dcde0
- source_dirty: True
- device_label: cloud&#45;api
- command: run&#45;model
- run_status: completed
- 경고: 실행 시 소스 작업 트리가 변경된 상태였습니다. 커밋만으로 재현을 보장하지 않으므로 실제 변경 내용과 suite/prompt 해시를 검토하세요.
- 요청 모델: gpt&#45;5&#46;6&#45;luna
- 프롬프트·테스트 suite SHA256 및 전체 설정: [manifest.json](manifest.json) (`prompt_sha256`, `suite_sha256`)
- gpt&#45;5&#46;6&#45;luna 자기보고 모델 카드 URL: 미기록; 라이선스 URL: 미기록 (팀 검증 필요)

### 고정 옵션
- num_ctx: 미기록
- num_predict: 2048
- temperature: 미기록
- seed: 미기록
- repeat_seeds: &#91;None, None&#93;
- retry_policy: none
- order: model, case, repeat
- history: reset each request; no context sent
- generation_api: /chat/completions
- cloud_controls: OpenAI&#45;compatible chat completions API; no local seed control&#46; This model rejects any non&#45;default temperature &#40;HTTP 400&#41;, so temperature is not sent and the model&#x27;s own default applies&#46; This run uses the full 10&#45;case x2&#45;repeat local&#45;style protocol, NOT the team&#x27;s fixed 5&#45;call Cloud comparison in docs/CLOUD&#46;md&#46;
- Python evaluator backend: python&#45;subprocess
- Python evaluator python_version: 3&#46;12&#46;13
- Python evaluator pytest_version: 8&#46;3&#46;5
- Python evaluator runner_hash: 3e35801a89df9d5e9e650202bd7a113014e2202ebe8694ad4d327a182a619177
- Python evaluator wall_timeout: 30&#46;0

### 실행 시 환경
- os: system=Windows; release=11; machine=AMD64
- cpu: architecture=AMD64; logical_count=24; name=미기록
- python_version: 3&#46;12&#46;13
- ram_bytes: 33752997888
- ram_unavailable_reason: 미기록
- nvidia_unavailable_reason: 미기록
- GPU: name=NVIDIA GeForce RTX 5060 Laptop GPU; memory_total_mib=8151&#46;0; driver_version=592&#46;01

## 완료 상태
전체: 완료; 누락 0; 인프라 오류 0. 계획된 기록 수집 완료.
not_run은 미실행이며 실패가 아닙니다. missing_response는 입력 누락입니다. 완료는 모든 풀이 성공을 뜻하지 않습니다.

| 모델 | solved/planned | call_successes/attempts | 두 반복 모두 해결/케이스 | 응답 품질 n | 완료 기록 | not_run | 입력 누락 | 인프라 오류 | 상태 |
|---|---|---|---|---|---|---|---|---|---|
| gpt&#45;5&#46;6&#45;luna | 20/20 | 20/20 | 10/10 | 20 | 20 | 0 | 0 | 0 | 완료 |

### 성공한 호출의 지표 평균 (각 유효 표본 n)
응답 품질 n은 추출/테스트 실패를 포함한 성공 호출 수입니다. 호출 실패는 평균에서 제외합니다. null은 측정 불가이며 0점이 아닙니다. timeout은 평가 제한시간 초과이며 인프라 오류로 단정하지 않습니다.
| 모델 | elapsed s (n) | loading s (n) | tokens/sec (n) | VRAM MiB (n) |
|---|---|---|---|---|
| gpt&#45;5&#46;6&#45;luna | 4.845 (n=20) | null (n=0) | null (n=0) | null (n=0) |

## Warmup (본 실험 통계에서 제외)
- gpt&#45;5&#46;6&#45;luna: 미기록; elapsed=미기록; 

## 케이스별 반복 상태 및 증거
원문·metadata·show·ps의 내용은 비밀정보 노출 방지를 위해 여기 펼치지 않습니다. 파일이 실제 존재할 때만 링크합니다.

### gpt&#45;5&#46;6&#45;luna
[metadata](model-1/metadata.json)

| case | repeat | status | 증거 |
|---|---|---|---|
| B01 | 1 | solved | [raw JSON](model-1/B01-r1.raw.json) · [solution](model-1/B01-r1.solution.py) · [pytest log](model-1/B01-r1.pytest.log) |
| B01 | 2 | solved | [raw JSON](model-1/B01-r2.raw.json) · [solution](model-1/B01-r2.solution.py) · [pytest log](model-1/B01-r2.pytest.log) |
| B02 | 1 | solved | [raw JSON](model-1/B02-r1.raw.json) · [solution](model-1/B02-r1.solution.py) · [pytest log](model-1/B02-r1.pytest.log) |
| B02 | 2 | solved | [raw JSON](model-1/B02-r2.raw.json) · [solution](model-1/B02-r2.solution.py) · [pytest log](model-1/B02-r2.pytest.log) |
| B03 | 1 | solved | [raw JSON](model-1/B03-r1.raw.json) · [solution](model-1/B03-r1.solution.py) · [pytest log](model-1/B03-r1.pytest.log) |
| B03 | 2 | solved | [raw JSON](model-1/B03-r2.raw.json) · [solution](model-1/B03-r2.solution.py) · [pytest log](model-1/B03-r2.pytest.log) |
| B04 | 1 | solved | [raw JSON](model-1/B04-r1.raw.json) · [solution](model-1/B04-r1.solution.py) · [pytest log](model-1/B04-r1.pytest.log) |
| B04 | 2 | solved | [raw JSON](model-1/B04-r2.raw.json) · [solution](model-1/B04-r2.solution.py) · [pytest log](model-1/B04-r2.pytest.log) |
| B05 | 1 | solved | [raw JSON](model-1/B05-r1.raw.json) · [solution](model-1/B05-r1.solution.py) · [pytest log](model-1/B05-r1.pytest.log) |
| B05 | 2 | solved | [raw JSON](model-1/B05-r2.raw.json) · [solution](model-1/B05-r2.solution.py) · [pytest log](model-1/B05-r2.pytest.log) |
| B06 | 1 | solved | [raw JSON](model-1/B06-r1.raw.json) · [solution](model-1/B06-r1.solution.py) · [pytest log](model-1/B06-r1.pytest.log) |
| B06 | 2 | solved | [raw JSON](model-1/B06-r2.raw.json) · [solution](model-1/B06-r2.solution.py) · [pytest log](model-1/B06-r2.pytest.log) |
| B07 | 1 | solved | [raw JSON](model-1/B07-r1.raw.json) · [solution](model-1/B07-r1.solution.py) · [pytest log](model-1/B07-r1.pytest.log) |
| B07 | 2 | solved | [raw JSON](model-1/B07-r2.raw.json) · [solution](model-1/B07-r2.solution.py) · [pytest log](model-1/B07-r2.pytest.log) |
| B08 | 1 | solved | [raw JSON](model-1/B08-r1.raw.json) · [solution](model-1/B08-r1.solution.py) · [pytest log](model-1/B08-r1.pytest.log) |
| B08 | 2 | solved | [raw JSON](model-1/B08-r2.raw.json) · [solution](model-1/B08-r2.solution.py) · [pytest log](model-1/B08-r2.pytest.log) |
| B09 | 1 | solved | [raw JSON](model-1/B09-r1.raw.json) · [solution](model-1/B09-r1.solution.py) · [pytest log](model-1/B09-r1.pytest.log) |
| B09 | 2 | solved | [raw JSON](model-1/B09-r2.raw.json) · [solution](model-1/B09-r2.solution.py) · [pytest log](model-1/B09-r2.pytest.log) |
| B10 | 1 | solved | [raw JSON](model-1/B10-r1.raw.json) · [solution](model-1/B10-r1.solution.py) · [pytest log](model-1/B10-r1.pytest.log) |
| B10 | 2 | solved | [raw JSON](model-1/B10-r2.raw.json) · [solution](model-1/B10-r2.solution.py) · [pytest log](model-1/B10-r2.pytest.log) |

---

> ⚠️ **아래 비교 섹션은 수동으로 추가한 내용입니다.** 위쪽은 `harness report`가 이 폴더의
> `manifest.json`/`results.jsonl`만으로 자동 생성한 것(gpt-5.6-luna 단일 모델)이고, 아래는 다른
> 실행(`results/chanyeongg3/20260915-qwen25-coder-7b/`)과 수동으로 나란히 정리한 것입니다.
> **`uv run python -m harness report`로 이 파일을 재생성하면 이 섹션은 사라집니다** — 재생성 시
> 이 섹션을 다시 붙여넣어야 합니다.

## 비교: qwen2.5-coder:7b vs gpt-5.6-luna

> 서로 다른 두 실행 — 팀 공식 제출 [`results/chanyeongg3/20260915-qwen25-coder-7b/`](../../chanyeongg3/20260915-qwen25-coder-7b/)와 이 폴더의 `gpt-5.6-luna` 실행 —
> 의 `summary.json`/`results.jsonl`을 나란히 정리했습니다. 하나의 manifest로 실행된 공식
> `run --models A B` 비교가 아니며, 참가자·장비·일부 생성 옵션이 다릅니다. 증거 원문은 중복
> 저장하지 않았으므로 각 모델의 원본 `results/` 경로에서 확인하세요.

### 실행 정보

| 항목 | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| participant | chanyeongg3 | cloud |
| 실행 경로 | `results/chanyeongg3/20260915-qwen25-coder-7b/` | `results/cloud/20260916-gpt5-6-luna/` |
| command | run-model | run-model (`scripts/cloud_run_model.py`) |
| device_label | rtx5070-8gb-local (오기, 실제로는 RTX 5060 Laptop) | cloud-api |

### 고정 옵션 (두 실행이 서로 다름 — 그대로 병기)

| 옵션 | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| num_ctx | 8192 | 미기록(해당 없음) |
| num_predict / max_completion_tokens | 2048 | 2048 |
| temperature | 0.2 | 미지원(모델이 HTTP 400으로 거부 — 기본값 사용) |
| seed / repeat_seeds | 42, 43 | 미지원(없음) |
| generation_api | /api/generate (Ollama) | /chat/completions (OpenAI 호환) |

### 완료 상태 비교

| 모델 | solved/planned | call_successes/attempts | 두 반복 모두 해결/케이스 | 응답 품질 n | not_run | 인프라 오류 |
|---|---|---|---|---|---|---|
| qwen2.5-coder:7b | 6/20 | 20/20 | 3/10 | 20 | 0 | 0 |
| gpt-5.6-luna | **20/20** | 20/20 | **10/10** | 20 | 0 | 0 |

### 성공한 호출의 지표 평균 비교 (각 유효 표본 n)

| 모델 | elapsed s (n) | loading s (n) | tokens/sec (n) | VRAM MiB (n) |
|---|---|---|---|---|
| qwen2.5-coder:7b | 2.225 (n=20) | 0.002 (n=20) | 66.227 (n=20) | 4756.100 (n=20) |
| gpt-5.6-luna | 4.845 (n=20) | null (n=0) | null (n=0) | null (n=0) |

### 케이스별 반복 상태 비교

| case | qwen2.5-coder 1회 | qwen2.5-coder 2회 | gpt-5.6-luna 1회 | gpt-5.6-luna 2회 |
|---|---|---|---|---|
| B01 | test_failure | test_failure | solved | solved |
| B02 | solved | solved | solved | solved |
| B03 | test_failure | test_failure | solved | solved |
| B04 | solved | solved | solved | solved |
| B05 | test_failure | test_failure | solved | solved |
| B06 | solved | solved | solved | solved |
| B07 | test_failure | test_failure | solved | solved |
| B08 | test_failure | test_failure | solved | solved |
| B09 | test_failure | test_failure | solved | solved |
| B10 | test_failure | test_failure | solved | solved |

### 해석 (비공식, 팀 검증 전)

gpt-5.6-luna가 10문제 20회 전부 해결(100%)해 qwen2.5-coder:7b(6/20, 30%)를 크게 앞섰다. qwen이
두 반복 모두 실패한 7문제(B01, B03, B05, B07, B08, B09, B10) 전부를 gpt-5.6-luna는 해결했다. 다만
비교 조건이 완전히 동일하지 않다: 클라우드는 temperature/seed를 제어할 수 없었고, 이 실행은
`docs/CLOUD.md`의 공식 5×1 Cloud 프로토콜이 아닌 20회 프로토콜이라 팀의 공식 결론으로 바로 쓸 수
없다. 자세한 한계는 [`NOTES.md`](NOTES.md)를 참고한다.
