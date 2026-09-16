# 비교 보고서: qwen2.5-coder:7b-instruct (로컬) vs gpt-5.6-luna (클라우드)

> ⚠️ **탐색 자료입니다. 팀 공식 Cloud 비교 결과가 아닙니다.**
> `docs/CLOUD.md`는 비용 통제를 위해 **사전 지정 5문제 × 1회**를 규정하지만, 이 보고서가 근거로 삼은
> luna 실행은 로컬과 동일한 **10문제 × 2회(20회)** 프로토콜로 수행되었습니다. 팀의 공식 모델 선정·
> 발제문 결론에는 `docs/CLOUD.md`의 5×1 결과를 사용하고, 이 문서는 참고용으로만 인용하세요.
>
> 또한 luna 실행 결과는 작성 시점에 `main`에 병합되어 있지 않습니다. 원본은 원격 브랜치
> `origin/results-cloud-gpt5.6-luna-20260916`의 `results/cloud/20260916-gpt5-6-luna/`에 있습니다.

## 근거 자료
| 모델 | 실행 폴더 | 위치 |
|---|---|---|
| qwen2.5-coder:7b-instruct | `results/chanyeongg3/20260915-qwen25-coder-7b/` | `main` |
| gpt-5.6-luna | `results/cloud/20260916-gpt5-6-luna/` | `origin/results-cloud-gpt5.6-luna-20260916` |

수치는 각 실행의 `summary.json`·`results.jsonl`에서, 실패 원인은 `model-1/*.pytest.log`에서 읽었습니다.

## 실행 조건

| 항목 | qwen2.5-coder:7b-instruct | gpt-5.6-luna |
|---|---|---|
| 문제 / 반복 | B01–B10 × 2회 (20회) | B01–B10 × 2회 (20회) |
| temperature | 0.2 | **미적용** (모델이 non-default 값을 HTTP 400으로 거부 → 모델 기본값) |
| seed | 42 / 43 | 제어 불가 |
| num_ctx / num_predict | 8192 / 2048 | 미기록 / 2048 |
| 생성 API | `/api/generate` (Ollama) | `/chat/completions` (OpenAI 호환) |
| 실행 위치 | 로컬 GPU (RTX 5060 Laptop, 8151 MiB) | 원격 클라우드 (로컬 GPU 무관) |
| 채점기 | python-subprocess, Python 3.12.13 / pytest 8.3.5 (동일) | 동일 |
| `source_dirty` | False | True (※ 아래 한계 참고) |

두 실행 모두 채점기 `runner_hash`가 `3e35801a…`로 동일하며, 호출 실패·형식 오류·인프라 오류는 양쪽 0건입니다.

## 결과 요약

| 지표 | qwen2.5-coder:7b-instruct | gpt-5.6-luna |
|---|---|---|
| **완전 해결 / 계획 20회** | **6/20 (30%)** | **20/20 (100%)** |
| 두 번 모두 해결 / 10문제 | 3/10 | 10/10 |
| 호출 성공 / 시도 | 20/20 | 20/20 |
| 실패 유형 | test_failure 14 | 없음 |
| 형식(추출) 오류 | 0 | 0 |
| 인프라 오류 | 0 | 0 |

## 문제별 반복 상태

| 문제 | 주제 | qwen 1회 | qwen 2회 | luna 1회 | luna 2회 |
|---|---|---|---|---|---|
| B01 | 금액 반올림 | test_failure | test_failure | solved | solved |
| B02 | 페이지네이션 | solved | solved | solved | solved |
| B03 | 선택 입력 검증 | test_failure | test_failure | solved | solved |
| B04 | 시간 범위 | solved | solved | solved | solved |
| B05 | 요청 멱등성 | test_failure | test_failure | solved | solved |
| B06 | 사용자별 캐시 | solved | solved | solved | solved |
| B07 | 부분 업데이트 | test_failure | test_failure | solved | solved |
| B08 | 재시도·부작용 | test_failure | test_failure | solved | solved |
| B09 | 객체 접근 권한 | test_failure | test_failure | solved | solved |
| B10 | 주문·재고 원자성 | test_failure | test_failure | solved | solved |

qwen이 해결한 3문제(B02·B04·B06)는 luna도 모두 해결했습니다. luna의 결과가 qwen의 상위집합이며,
두 모델이 갈린 문제는 7개입니다. 반복 간 결과가 흔들린 문제(한 번만 해결)는 **양쪽 모두 0건**으로,
qwen의 실패는 표본 운이 아니라 반복 재현되는 결정적 실패입니다.

## qwen 실패 7문제의 성격

실패한 문제는 대부분 **공개 테스트는 통과하고 hidden 테스트에서만 깨졌습니다** (B07만 예외로
`test_public.py::test_name`도 실패). 근거는 `results/chanyeongg3/20260915-qwen25-coder-7b/model-1/B*-r1.pytest.log`입니다.

| 문제 | 통과/실패 | 대표 실패 테스트 | 원인 분류 |
|---|---|---|---|
| B01 | 7 passed / 3 failed | `test_no_rounding_carry_between_lines`, `test_input_and_context_unchanged` | 항목별 정밀도, 입력 불변성 |
| B03 | 6 passed / 4 failed | `test_invalid_limits`·`test_invalid_offsets` (`DID NOT RAISE ValueError`) | 검증·거부 분기 누락 |
| B05 | 8 passed / 2 failed | `test_input_snapshot_and_no_input_mutation`, `test_return_values_are_independent` | 입력 변형, 반환값 공유 |
| B07 | 5 passed / 5 failed | `test_public.py::test_name`, `test_null`, `test_false` | 누락/null/falsy 구분 실패 |
| B08 | 6 passed / 4 failed | `test_before_retry`, `test_permanent_immediate` (`DID NOT RAISE`) | 부작용 중복, 오류 분류 |
| B09 | 9 passed / 1 failed | `test_cancelled_still_private` (`DID NOT RAISE`) | 거부 시 상태 처리 |
| B10 | 7 passed / 3 failed | `test_after_stock_rollback`, `test_after_order_rollback` | 다단계 실패 복구 |

정리하면 실패 원인은 알고리즘 난이도가 아니라 **명세의 암묵적 계약을 지키지 못하는 것**입니다.
① 검증·오류 발생 분기 누락(B03·B08·B09), ② 입력 불변성·반환값 독립성 위반(B01·B05),
③ 다단계 상태 롤백 실패(B08·B10) 세 갈래로 묶입니다.

B01의 경우 qwen은 합계를 한 번만 반올림해 `test_no_rounding_carry_between_lines`에서 깨졌고,
luna는 항목별로 `Decimal.quantize(..., ROUND_HALF_UP)`를 적용한 뒤 합산해 통과했습니다
(`results/cloud/20260916-gpt5-6-luna/model-1/B01-r1.solution.py`). 팀의 다른 탐색 보고서에 따르면
codellama:7b·deepseek-coder:6.7b-instruct도 같은 지점에서 실패했습니다
([docs/EXPLORATORY_REPORT_qwen_vs_codellama.md](../../docs/EXPLORATORY_REPORT_qwen_vs_codellama.md),
[docs/EXPLORATORY_REPORT_qwen_vs_deepseek.md](../../docs/EXPLORATORY_REPORT_qwen_vs_deepseek.md)).

## 성능 지표 (⚠️ 직접 비교 불가)

| 지표 | qwen2.5-coder:7b-instruct | gpt-5.6-luna |
|---|---|---|
| 평균 응답 시간 (n=20) | 2.225s | 4.845s |
| 최소 / 최대 응답 시간 | 1.19s / 4.83s | 1.81s / 12.14s |
| 20회 합계 호출 시간 | 44.5s | 96.9s |
| 평균 로딩 시간 (n=20) | 0.002s | 측정 불가 (n=0) |
| 생성 속도 | 66.23 tokens/s (n=20) | 측정 불가 (n=0) |
| 평균 VRAM (n=20) | 4756 MiB | 해당 없음 (원격 실행) |
| 출력 토큰 합계 | 2,683 | 6,567 (추론 토큰 3,580 포함) |
| 입력 토큰 합계 | 미집계 | 15,890 |

**이 표로 속도 우열을 판단하면 안 됩니다.** qwen은 로컬 GPU 추론, luna는 네트워크 왕복을 포함한
원격 호출이라 측정 축 자체가 다릅니다. `REPORT.md`도 서로 다른 환경 간 속도 비교는 의미가 없다고
명시합니다.

의미 있는 관찰은 토큰 쪽입니다. luna는 qwen의 약 2.4배 출력 토큰을 사용했고 그중 절반 이상(3,580)이
추론 토큰입니다. 100% 정확도가 **추론 예산을 더 소비한 결과**로 보입니다. 실제 과금 단가는 미확인이며
팀이 채워야 합니다. tokens/s·VRAM의 `null`은 측정 불가이지 0점이 아닙니다.

## 한계

1. **샘플링 조건 불일치.** luna는 temperature·seed를 고정하지 못했습니다(모델이 non-default temperature를
   HTTP 400으로 거부). 로컬과 완전히 동일한 확률적 조건이 아닙니다.
2. **재현성 미확인.** luna는 seed를 바꾼 반복 실행을 하지 않아, 20/20이 다른 조건에서도 유지되는지
   검증되지 않았습니다.
3. **비공식 프로토콜.** 위 경고대로 `docs/CLOUD.md`의 5문제×1회 규약을 따르지 않아 API 비용이 약 4배
   발생했습니다. 공식 결론에는 사용할 수 없습니다.
4. **모델 카드·라이선스 미확인.** `gpt-5.6-luna`는 공개 모델 카드 URL을 특정할 수 없습니다(수업 제공
   프록시 모델명으로 추정). 이용 약관·사용 목적 적합성을 팀이 직접 확인해야 합니다.
5. **`source_dirty: True`.** luna 실행 당시 `scripts/cloud_run_model.py`가 미커밋 신규 파일이었기 때문이며,
   `harness/core.py` 등 채점 로직이 변경된 상태는 아니었습니다. 20건 모두 모델이 fenced 코드 블록
   하나만 반환해 코드 추출 규칙 차이의 영향은 없었습니다.
6. **표본 크기.** 10문제·2반복으로는 통계적 우위를 단정할 수 없습니다([docs/EXPERIMENT.md](../../docs/EXPERIMENT.md) 참고).

## 결론

동일한 10문제·2회 조건에서 **30%(6/20) 대 100%(20/20)**, 격차 70%p입니다. 차이는 알고리즘 난이도가
아니라 hidden 테스트가 검증하는 계약 준수(불변성·오류 처리·원자성)에서 발생했고, 이는 7B급 로컬
모델이 구조적으로 약한 지점과 일치합니다.

다만 샘플링 조건 불일치·단일 실행·비공식 프로토콜이라는 세 한계 때문에, "luna가 완벽하다"보다는
**"현재 조건에서 로컬 7B급 모델로는 이 스위트를 통과하기 어렵다"**는 쪽이 방어 가능한 결론입니다.
공식 Cloud 비교는 `docs/CLOUD.md`의 5문제×1회 프로토콜로 별도 수행해야 합니다.

## 보안 점검
`results/cloud/` 전체 스캔 결과 API 키·Authorization 헤더·Windows 사용자명 패턴은 탐지되지 않았습니다.
프롬프트에는 공개 벤치마크 코드만 포함됩니다. 생성 코드는 현재 사용자 권한으로 파일시스템·네트워크에
접근하며, 임시 디렉터리·Python `-I`·시간 제한은 보안 격리가 아닙니다.
