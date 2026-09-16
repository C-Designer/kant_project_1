# 실행 결과 (자동 생성)

> ⚠️ **비공식 탐색 실행 — Docker 미사용**: 이 장비에는 Docker Desktop/WSL2가 설치되어 있지 않아, 프로젝트가 요구하는 컨테이너 격리(`harness/docker_runner.py`, 네트워크·자원 제한) 없이 생성 코드를 호스트 서브프로세스에서 직접 실행해 채점했습니다. prompt 생성·코드 추출·pytest 판정 로직 자체는 공식 harness와 동일하지만, 격리 없이 실행했으므로 팀 공식 비교(`results/<participant>/<run-id>`)로 제출하기 전에 Docker 환경에서 재검증이 필요합니다.

수치는 자동 계산입니다. 해석은 [NOTES.md](NOTES.md)에 사람이 작성해야 하며 이 보고서는 해석 완료를 주장하지 않습니다.

서로 다른 PC 간 속도 비교는 의미가 없습니다. 공식 두 모델 동일 PC 비교와 클라우드 5×1 실험은 별도 팀 의무입니다.
결과는 results/<participant>/<run-id> 아래 Git 추적 대상으로 보관합니다. 원문 공개 전 키·개인정보를 확인하세요.

## 실행 정보

Execution warning: Generated code runs as the current user with filesystem and network access. A temporary directory, Python -I, and a subprocess wall-time limit are not security isolation. No RAM, CPU, network, or filesystem isolation is provided. Hidden tests and runner output are not protected against adversarial code.
- participant: 미기록
- created_utc: 2026&#45;09&#45;15T04:11:39Z
- source_commit: 미기록
- source_dirty: 미기록
- device_label: 미기록
- command: run
- run_status: completed
- 요청 모델: qwen2&#46;5&#45;coder:7b, deepseek&#45;coder:6&#46;7b&#45;instruct
- 프롬프트·테스트 suite SHA256 및 전체 설정: [manifest.json](manifest.json) (`prompt_sha256`, `suite_sha256`)
- qwen2&#46;5&#45;coder:7b 자기보고 모델 카드 URL: 미기록; 라이선스 URL: 미기록 (팀 검증 필요)
- deepseek&#45;coder:6&#46;7b&#45;instruct 자기보고 모델 카드 URL: 미기록; 라이선스 URL: 미기록 (팀 검증 필요)

### 고정 옵션
- num_ctx: 8192
- num_predict: 2048
- temperature: 0&#46;2
- seed: 42
- repeat_seeds: &#91;42, 43&#93;
- retry_policy: 미기록
- order: 미기록
- history: 미기록
- generation_api: 미기록
- cloud_controls: 미기록
- Python evaluator backend: 미기록
- Python evaluator python_version: 미기록
- Python evaluator pytest_version: 미기록
- Python evaluator runner_hash: 미기록
- Python evaluator wall_timeout: 미기록

### 실행 시 환경
- 환경: 미기록 (보고서 재생성 장치로 대체하지 않음)

## 완료 상태
전체: 완료; 누락 0; 인프라 오류 0. 계획된 기록 수집 완료.
not_run은 미실행이며 실패가 아닙니다. missing_response는 입력 누락입니다. 완료는 모든 풀이 성공을 뜻하지 않습니다.

| 모델 | solved/planned | call_successes/attempts | 두 반복 모두 해결/케이스 | 응답 품질 n | 완료 기록 | not_run | 입력 누락 | 인프라 오류 | 상태 |
|---|---|---|---|---|---|---|---|---|---|
| qwen2&#46;5&#45;coder:7b | 6/20 | 20/20 | 3/10 | 20 | 20 | 0 | 0 | 0 | 완료 |
| deepseek&#45;coder:6&#46;7b&#45;instruct | 2/20 | 20/20 | 1/10 | 20 | 20 | 0 | 0 | 0 | 완료 |

### 성공한 호출의 지표 평균 (각 유효 표본 n)
응답 품질 n은 추출/테스트 실패를 포함한 성공 호출 수입니다. 호출 실패는 평균에서 제외합니다. null은 측정 불가이며 0점이 아닙니다. timeout은 평가 제한시간 초과이며 인프라 오류로 단정하지 않습니다.
| 모델 | elapsed s (n) | loading s (n) | tokens/sec (n) | VRAM MiB (n) |
|---|---|---|---|---|
| qwen2&#46;5&#45;coder:7b | 2.305 (n=20) | 0.003 (n=20) | 60.775 (n=20) | 4756.100 (n=20) |
| deepseek&#45;coder:6&#46;7b&#45;instruct | 7.699 (n=20) | 0.003 (n=20) | 28.083 (n=20) | 5942.630 (n=20) |

## Warmup (본 실험 통계에서 제외)
- qwen2&#46;5&#45;coder:7b: 미기록; elapsed=미기록; [warmup 원문](model-1/warmup.raw.json)
- deepseek&#45;coder:6&#46;7b&#45;instruct: 미기록; elapsed=미기록; [warmup 원문](model-2/warmup.raw.json)

## 케이스별 반복 상태 및 증거
원문·metadata·show·ps의 내용은 비밀정보 노출 방지를 위해 여기 펼치지 않습니다. 파일이 실제 존재할 때만 링크합니다.

### qwen2&#46;5&#45;coder:7b
메타데이터/모델 show: 미기록

| case | repeat | status | 증거 |
|---|---|---|---|
| B01 | 1 | test&#95;failure | [raw JSON](model-1/B01-r1.raw.json) · [solution](model-1/B01-r1.solution.py) · [pytest log](model-1/B01-r1.pytest.log) · [ps](model-1/B01-r1.ps.json) |
| B01 | 2 | test&#95;failure | [raw JSON](model-1/B01-r2.raw.json) · [solution](model-1/B01-r2.solution.py) · [pytest log](model-1/B01-r2.pytest.log) · [ps](model-1/B01-r2.ps.json) |
| B02 | 1 | solved | [raw JSON](model-1/B02-r1.raw.json) · [solution](model-1/B02-r1.solution.py) · [pytest log](model-1/B02-r1.pytest.log) · [ps](model-1/B02-r1.ps.json) |
| B02 | 2 | solved | [raw JSON](model-1/B02-r2.raw.json) · [solution](model-1/B02-r2.solution.py) · [pytest log](model-1/B02-r2.pytest.log) · [ps](model-1/B02-r2.ps.json) |
| B03 | 1 | test&#95;failure | [raw JSON](model-1/B03-r1.raw.json) · [solution](model-1/B03-r1.solution.py) · [pytest log](model-1/B03-r1.pytest.log) · [ps](model-1/B03-r1.ps.json) |
| B03 | 2 | test&#95;failure | [raw JSON](model-1/B03-r2.raw.json) · [solution](model-1/B03-r2.solution.py) · [pytest log](model-1/B03-r2.pytest.log) · [ps](model-1/B03-r2.ps.json) |
| B04 | 1 | solved | [raw JSON](model-1/B04-r1.raw.json) · [solution](model-1/B04-r1.solution.py) · [pytest log](model-1/B04-r1.pytest.log) · [ps](model-1/B04-r1.ps.json) |
| B04 | 2 | solved | [raw JSON](model-1/B04-r2.raw.json) · [solution](model-1/B04-r2.solution.py) · [pytest log](model-1/B04-r2.pytest.log) · [ps](model-1/B04-r2.ps.json) |
| B05 | 1 | test&#95;failure | [raw JSON](model-1/B05-r1.raw.json) · [solution](model-1/B05-r1.solution.py) · [pytest log](model-1/B05-r1.pytest.log) · [ps](model-1/B05-r1.ps.json) |
| B05 | 2 | test&#95;failure | [raw JSON](model-1/B05-r2.raw.json) · [solution](model-1/B05-r2.solution.py) · [pytest log](model-1/B05-r2.pytest.log) · [ps](model-1/B05-r2.ps.json) |
| B06 | 1 | solved | [raw JSON](model-1/B06-r1.raw.json) · [solution](model-1/B06-r1.solution.py) · [pytest log](model-1/B06-r1.pytest.log) · [ps](model-1/B06-r1.ps.json) |
| B06 | 2 | solved | [raw JSON](model-1/B06-r2.raw.json) · [solution](model-1/B06-r2.solution.py) · [pytest log](model-1/B06-r2.pytest.log) · [ps](model-1/B06-r2.ps.json) |
| B07 | 1 | test&#95;failure | [raw JSON](model-1/B07-r1.raw.json) · [solution](model-1/B07-r1.solution.py) · [pytest log](model-1/B07-r1.pytest.log) · [ps](model-1/B07-r1.ps.json) |
| B07 | 2 | test&#95;failure | [raw JSON](model-1/B07-r2.raw.json) · [solution](model-1/B07-r2.solution.py) · [pytest log](model-1/B07-r2.pytest.log) · [ps](model-1/B07-r2.ps.json) |
| B08 | 1 | test&#95;failure | [raw JSON](model-1/B08-r1.raw.json) · [solution](model-1/B08-r1.solution.py) · [pytest log](model-1/B08-r1.pytest.log) · [ps](model-1/B08-r1.ps.json) |
| B08 | 2 | test&#95;failure | [raw JSON](model-1/B08-r2.raw.json) · [solution](model-1/B08-r2.solution.py) · [pytest log](model-1/B08-r2.pytest.log) · [ps](model-1/B08-r2.ps.json) |
| B09 | 1 | test&#95;failure | [raw JSON](model-1/B09-r1.raw.json) · [solution](model-1/B09-r1.solution.py) · [pytest log](model-1/B09-r1.pytest.log) · [ps](model-1/B09-r1.ps.json) |
| B09 | 2 | test&#95;failure | [raw JSON](model-1/B09-r2.raw.json) · [solution](model-1/B09-r2.solution.py) · [pytest log](model-1/B09-r2.pytest.log) · [ps](model-1/B09-r2.ps.json) |
| B10 | 1 | test&#95;failure | [raw JSON](model-1/B10-r1.raw.json) · [solution](model-1/B10-r1.solution.py) · [pytest log](model-1/B10-r1.pytest.log) · [ps](model-1/B10-r1.ps.json) |
| B10 | 2 | test&#95;failure | [raw JSON](model-1/B10-r2.raw.json) · [solution](model-1/B10-r2.solution.py) · [pytest log](model-1/B10-r2.pytest.log) · [ps](model-1/B10-r2.ps.json) |

### deepseek&#45;coder:6&#46;7b&#45;instruct
메타데이터/모델 show: 미기록

| case | repeat | status | 증거 |
|---|---|---|---|
| B01 | 1 | test&#95;failure | [raw JSON](model-2/B01-r1.raw.json) · [solution](model-2/B01-r1.solution.py) · [pytest log](model-2/B01-r1.pytest.log) · [ps](model-2/B01-r1.ps.json) |
| B01 | 2 | test&#95;failure | [raw JSON](model-2/B01-r2.raw.json) · [solution](model-2/B01-r2.solution.py) · [pytest log](model-2/B01-r2.pytest.log) · [ps](model-2/B01-r2.ps.json) |
| B02 | 1 | test&#95;failure | [raw JSON](model-2/B02-r1.raw.json) · [solution](model-2/B02-r1.solution.py) · [pytest log](model-2/B02-r1.pytest.log) · [ps](model-2/B02-r1.ps.json) |
| B02 | 2 | test&#95;failure | [raw JSON](model-2/B02-r2.raw.json) · [solution](model-2/B02-r2.solution.py) · [pytest log](model-2/B02-r2.pytest.log) · [ps](model-2/B02-r2.ps.json) |
| B03 | 1 | test&#95;failure | [raw JSON](model-2/B03-r1.raw.json) · [solution](model-2/B03-r1.solution.py) · [pytest log](model-2/B03-r1.pytest.log) · [ps](model-2/B03-r1.ps.json) |
| B03 | 2 | test&#95;failure | [raw JSON](model-2/B03-r2.raw.json) · [solution](model-2/B03-r2.solution.py) · [pytest log](model-2/B03-r2.pytest.log) · [ps](model-2/B03-r2.ps.json) |
| B04 | 1 | test&#95;failure | [raw JSON](model-2/B04-r1.raw.json) · [solution](model-2/B04-r1.solution.py) · [pytest log](model-2/B04-r1.pytest.log) · [ps](model-2/B04-r1.ps.json) |
| B04 | 2 | test&#95;failure | [raw JSON](model-2/B04-r2.raw.json) · [solution](model-2/B04-r2.solution.py) · [pytest log](model-2/B04-r2.pytest.log) · [ps](model-2/B04-r2.ps.json) |
| B05 | 1 | test&#95;failure | [raw JSON](model-2/B05-r1.raw.json) · [solution](model-2/B05-r1.solution.py) · [pytest log](model-2/B05-r1.pytest.log) · [ps](model-2/B05-r1.ps.json) |
| B05 | 2 | test&#95;failure | [raw JSON](model-2/B05-r2.raw.json) · [solution](model-2/B05-r2.solution.py) · [pytest log](model-2/B05-r2.pytest.log) · [ps](model-2/B05-r2.ps.json) |
| B06 | 1 | solved | [raw JSON](model-2/B06-r1.raw.json) · [solution](model-2/B06-r1.solution.py) · [pytest log](model-2/B06-r1.pytest.log) · [ps](model-2/B06-r1.ps.json) |
| B06 | 2 | solved | [raw JSON](model-2/B06-r2.raw.json) · [solution](model-2/B06-r2.solution.py) · [pytest log](model-2/B06-r2.pytest.log) · [ps](model-2/B06-r2.ps.json) |
| B07 | 1 | test&#95;failure | [raw JSON](model-2/B07-r1.raw.json) · [solution](model-2/B07-r1.solution.py) · [pytest log](model-2/B07-r1.pytest.log) · [ps](model-2/B07-r1.ps.json) |
| B07 | 2 | test&#95;failure | [raw JSON](model-2/B07-r2.raw.json) · [solution](model-2/B07-r2.solution.py) · [pytest log](model-2/B07-r2.pytest.log) · [ps](model-2/B07-r2.ps.json) |
| B08 | 1 | test&#95;failure | [raw JSON](model-2/B08-r1.raw.json) · [solution](model-2/B08-r1.solution.py) · [pytest log](model-2/B08-r1.pytest.log) · [ps](model-2/B08-r1.ps.json) |
| B08 | 2 | test&#95;failure | [raw JSON](model-2/B08-r2.raw.json) · [solution](model-2/B08-r2.solution.py) · [pytest log](model-2/B08-r2.pytest.log) · [ps](model-2/B08-r2.ps.json) |
| B09 | 1 | test&#95;failure | [raw JSON](model-2/B09-r1.raw.json) · [solution](model-2/B09-r1.solution.py) · [pytest log](model-2/B09-r1.pytest.log) · [ps](model-2/B09-r1.ps.json) |
| B09 | 2 | test&#95;failure | [raw JSON](model-2/B09-r2.raw.json) · [solution](model-2/B09-r2.solution.py) · [pytest log](model-2/B09-r2.pytest.log) · [ps](model-2/B09-r2.ps.json) |
| B10 | 1 | test&#95;failure | [raw JSON](model-2/B10-r1.raw.json) · [solution](model-2/B10-r1.solution.py) · [pytest log](model-2/B10-r1.pytest.log) · [ps](model-2/B10-r1.ps.json) |
| B10 | 2 | test&#95;failure | [raw JSON](model-2/B10-r2.raw.json) · [solution](model-2/B10-r2.solution.py) · [pytest log](model-2/B10-r2.pytest.log) · [ps](model-2/B10-r2.ps.json) |
