# 비교 보고서: qwen2.5-coder:7b(로컬) vs gpt-5.6-luna(Cloud)

> ⚠️ **비공식 결과입니다.** 두 결과 모두 실제 실행 산출물에서 가져온 수치이지만, 클라우드 쪽은
> `docs/CLOUD.md`가 정한 고정 5문제×1회가 아니라 **로컬과 동일한 10문제×2회(20회) 프로토콜**로
> 실행되어 팀의 공식 Cloud 비교 방식과 다릅니다(비용 약 4배). 자세한 한계는
> [`results/cloud/20260916-gpt5-6-luna/NOTES.md`](../results/cloud/20260916-gpt5-6-luna/NOTES.md)를
> 참고하세요.
>
> - qwen2.5-coder:7b 출처: [`results/chanyeongg3/20260915-qwen25-coder-7b/`](../results/chanyeongg3/20260915-qwen25-coder-7b/) (팀 공식 제출, `run-model`, 로컬 RTX 5060 Laptop)
> - gpt-5.6-luna 출처: [`results/cloud/20260916-gpt5-6-luna/`](../results/cloud/20260916-gpt5-6-luna/) (`scripts/cloud_run_model.py`, OpenAI 호환 Chat Completions API)

## 한눈에 보는 평가 지표

| 평가 지표 | qwen2.5-coder:7b (로컬) | gpt-5.6-luna (Cloud) |
|---|---|---|
| 완전 해결 / 계획 | 6/20 (30%) | **20/20 (100%)** |
| 두 번 모두 해결한 문제 | 3/10 (B02, B04, B06) | **10/10 (전 문제)** |
| 호출 성공 / 시도 | 20/20 (100%) | 20/20 (100%) |
| 인프라 오류 | 0 | 0 |
| 형식(코드 추출) 실패 | 0/20 | 0/20 |
| 평균 응답 시간 | **2.23초** (n=20) | 4.85초 (n=20) — 네트워크 왕복 포함 |
| 평균 생성 속도 | 66.2 tokens/s | 측정 불가 (Cloud는 토큰/초 미제공) |
| 평균 VRAM | 4,756 MiB | 해당 없음 (원격 실행) |
| 평균 입력 토큰 | 미기록 (하니스가 로컬 prompt 토큰 수를 남기지 않음) | 794.5 (20회 합계 15,890) |
| 평균 출력 토큰 | 미기록 | 328.4 (그중 추론 토큰 179.0, 20회 합계 6,567 / 3,580) |
| 실행 비용 | 전기료 외 없음 | 실제 API 과금 발생 (단가 미확인 — 팀 확인 필요) |
| 샘플링 설정 | temperature=0.2, seed=42/43 고정 | temperature 커스텀 값 미지원(HTTP 400) → 모델 기본값 사용, seed 없음 |
| 라이선스 | Apache License 2.0 (확인 완료) | 미확인 — 모델 카드/이용 약관 팀 확인 필요 |
| 실행 방식 | `run-model` (팀 공식) | `cloud_run_model.py` (비공식, 10×2 프로토콜) |

## 문제별 결과 (10문제 × 2회)

| 문제 | qwen2.5-coder 1회차 | qwen2.5-coder 2회차 | gpt-5.6-luna 1회차 | gpt-5.6-luna 2회차 |
|---|---|---|---|---|
| B01 | test_failure | test_failure | **solved** | **solved** |
| B02 | solved | solved | **solved** | **solved** |
| B03 | test_failure | test_failure | **solved** | **solved** |
| B04 | solved | solved | **solved** | **solved** |
| B05 | test_failure | test_failure | **solved** | **solved** |
| B06 | solved | solved | **solved** | **solved** |
| B07 | test_failure | test_failure | **solved** | **solved** |
| B08 | test_failure | test_failure | **solved** | **solved** |
| B09 | test_failure | test_failure | **solved** | **solved** |
| B10 | test_failure | test_failure | **solved** | **solved** |

## 해석 (비공식, 팀 검증 전)
gpt-5.6-luna는 10문제 20회 전부를 통과해 qwen2.5-coder:7b(6/20)를 큰 폭으로 앞섰습니다. 특히
qwen이 둘 다 실패한 B01(항목별 반올림), B08(재시도), B10(재고 원자성)처럼 여러 단계의 상태·예외
처리가 얽힌 문제에서 격차가 뚜렷합니다. 반면 로컬은 응답이 약 2.2배 빠르고 전기료 외 비용이
없으며, 실행 조건(temperature, seed)을 그대로 고정할 수 있었던 반면 클라우드는 모델이 커스텀
temperature를 거부해 완전히 동일한 샘플링 조건은 아니었습니다.

이 비교는 **팀의 공식 Cloud 5문제 비교가 아니며**, 라이선스·실제 과금 단가도 미확인 상태입니다.
팀의 최종 모델 선정과 Cloud 도입 권고에는 `docs/CLOUD.md`의 고정 5×1 프로토콜 결과와 실제 비용
확인이 필요합니다.
