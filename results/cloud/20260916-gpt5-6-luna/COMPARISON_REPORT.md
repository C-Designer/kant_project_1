# 비교 실행 결과: qwen2.5-coder:7b vs gpt-5.6-luna

> ⚠️ **비공식 비교 문서입니다.** 이 파일은 하니스가 자동 생성한 것이 아니라, 서로 다른 두 실행 —
> 팀 공식 제출 [`results/chanyeongg3/20260915-qwen25-coder-7b/`](../../chanyeongg3/20260915-qwen25-coder-7b/)와
> 이 폴더의 `gpt-5.6-luna` 실행 — 의 `summary.json`/`results.jsonl`을 나란히 정리한 수동 비교표입니다.
> 두 실행은 **참가자·장비·일부 생성 옵션이 다른 별도 실행**이며, 하나의 manifest로 실행된 공식
> `run --models A B` 비교가 아닙니다. 증거 원문(raw JSON·solution.py·pytest log)은 중복 저장하지
> 않았으므로 아래 각 모델의 원본 `results/` 경로에서 직접 확인하세요.

## 실행 정보

| 항목 | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| participant | chanyeongg3 | cloud |
| 실행 경로 | `results/chanyeongg3/20260915-qwen25-coder-7b/` | `results/cloud/20260916-gpt5-6-luna/` |
| command | run-model | run-model (`scripts/cloud_run_model.py`) |
| created_utc | 2026-09-15 | 2026-09-16T06:48:44Z |
| device_label | rtx5070-8gb-local (오기, 실제로는 RTX 5060 Laptop) | cloud-api |
| run_status | completed | completed |

## 고정 옵션 (두 실행이 서로 다름 — 그대로 병기)

| 옵션 | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| num_ctx | 8192 | 미기록(해당 없음) |
| num_predict / max_completion_tokens | 2048 | 2048 |
| temperature | 0.2 | 미지원(모델이 HTTP 400으로 거부 — 기본값 사용) |
| seed / repeat_seeds | 42, 43 | 미지원(없음) |
| generation_api | /api/generate (Ollama) | /chat/completions (OpenAI 호환) |

## 완료 상태

| 모델 | solved/planned | call_successes/attempts | 두 반복 모두 해결/케이스 | 응답 품질 n | not_run | 인프라 오류 | 상태 |
|---|---|---|---|---|---|---|---|
| qwen2.5-coder:7b | 6/20 | 20/20 | 3/10 | 20 | 0 | 0 | 완료 |
| gpt-5.6-luna | **20/20** | 20/20 | **10/10** | 20 | 0 | 0 | 완료 |

## 성공한 호출의 지표 평균 (각 유효 표본 n)

| 모델 | elapsed s (n) | loading s (n) | tokens/sec (n) | VRAM MiB (n) |
|---|---|---|---|---|
| qwen2.5-coder:7b | 2.225 (n=20) | 0.002 (n=20) | 66.227 (n=20) | 4756.100 (n=20) |
| gpt-5.6-luna | 4.845 (n=20) | null (n=0) | null (n=0) | null (n=0) |

## 케이스별 반복 상태 (증거 링크는 각 모델의 원본 results/ 경로 참고)

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

증거 원문:
- qwen2.5-coder:7b: `results/chanyeongg3/20260915-qwen25-coder-7b/model-1/<CASE>-r<N>.{raw.json,solution.py,pytest.log,ps.json}`
- gpt-5.6-luna: `results/cloud/20260916-gpt5-6-luna/model-1/<CASE>-r<N>.{raw.json,solution.py,pytest.log}`

## 해석 (비공식, 팀 검증 전)
gpt-5.6-luna가 10문제 20회 전부 해결(100%)해 qwen2.5-coder:7b(6/20, 30%)를 크게 앞섰다. qwen이
두 반복 모두 실패한 7문제(B01, B03, B05, B07, B08, B09, B10) 전부를 gpt-5.6-luna는 해결했다. 다만
비교 조건이 완전히 동일하지 않다: 클라우드는 temperature/seed를 제어할 수 없었고, 이 실행은
`docs/CLOUD.md`의 공식 5×1 Cloud 프로토콜이 아닌 20회 프로토콜이라 팀의 공식 결론으로 바로 쓸 수
없다. 자세한 한계는 [`NOTES.md`](NOTES.md)를 참고한다.
