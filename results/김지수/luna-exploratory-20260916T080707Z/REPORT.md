# 실행 결과 (자동 생성)

수치는 자동 계산입니다. 해석은 [NOTES.md](NOTES.md)에 사람이 작성해야 하며 이 보고서는 해석 완료를 주장하지 않습니다.

서로 다른 PC 간 속도 비교는 의미가 없습니다. 공식 두 모델 동일 PC 비교와 클라우드 5×1 실험은 별도 팀 의무입니다.
결과는 results/<participant>/<run-id> 아래 Git 추적 대상으로 보관합니다. 원문 공개 전 키·개인정보를 확인하세요.

## 실행 정보

Execution warning: Generated code runs as the current user with filesystem and network access. A temporary directory, Python -I, and a subprocess wall-time limit are not security isolation. No RAM, CPU, network, or filesystem isolation is provided. Hidden tests and runner output are not protected against adversarial code.
- participant: 미기록
- created_utc: 2026&#45;09&#45;16T08:07:07&#46;132877&#43;00:00
- source_commit: e895b6389dd799314eec14815cf3df9bc25814a4
- source_dirty: True
- device_label: 미기록
- command: cloud&#45;run
- run_status: completed
- 경고: 실행 시 소스 작업 트리가 변경된 상태였습니다. 커밋만으로 재현을 보장하지 않으므로 실제 변경 내용과 suite/prompt 해시를 검토하세요.
- 요청 모델: gpt&#45;5&#46;6&#45;luna
- 프롬프트·테스트 suite SHA256 및 전체 설정: [manifest.json](manifest.json) (`prompt_sha256`, `suite_sha256`)
- gpt&#45;5&#46;6&#45;luna 자기보고 모델 카드 URL: 미기록; 라이선스 URL: 미기록 (팀 검증 필요)

### 고정 옵션
- num_ctx: 미기록
- num_predict: 미기록
- temperature: 미기록
- seed: 미기록
- repeat_seeds: not available; Responses API has no seed parameter
- retry_policy: none
- order: model, case, repeat
- history: reset each request; no previous&#95;response&#95;id sent
- generation_api: OpenAI Responses API &#40;client&#46;responses&#46;create&#41;
- cloud_controls: model=gpt&#45;5&#46;6&#45;luna; reasoning&#46;effort=none; max&#95;output&#95;tokens=2048; tools=&#91;&#93;; tool&#95;choice=none; store=False; temperature NOT set by the class&#45;provided script so the server default applied &#40;reported temperature=1&#46;0, top&#95;p=0&#46;98&#41; while local used temperature=0&#46;2; temperature IS settable on this endpoint; seed is not supported by the Responses API
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
| gpt&#45;5&#46;6&#45;luna | null (n=0) | null (n=0) | null (n=0) | null (n=0) |

## Warmup (본 실험 통계에서 제외)
- gpt&#45;5&#46;6&#45;luna: 미기록; elapsed=미기록; 

## 케이스별 반복 상태 및 증거
원문·metadata·show·ps의 내용은 비밀정보 노출 방지를 위해 여기 펼치지 않습니다. 파일이 실제 존재할 때만 링크합니다.

### gpt&#45;5&#46;6&#45;luna
메타데이터/모델 show: 미기록

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
