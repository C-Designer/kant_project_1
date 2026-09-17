# 팀 종합 비교 및 최종 모델 선정 보고서

> **2026-09-17 팀 최종본.** 이 문서는 `results/` 아래 커밋된 실행 산출물(`summary.json`, `results.jsonl`, `manifest.json`, `model-1/*.raw.json`, `*.pytest.log`)과 각 참가자의 `NOTES.md`, `docs/EXPLORATORY_REPORT_*.md`를 근거로 작성했습니다. 이 문서에 없는 수치를 새로 만들지 않았으며, 근거가 없는 항목은 **미확인**으로 남겼습니다. 양식은 [RESULTS_TEMPLATE.md](RESULTS_TEMPLATE.md)를 따릅니다.

## 0. 한 줄 결론

서로 다른 로컬 코딩 모델 3개(qwen2.5-coder:7b, deepseek-coder:6.7b-instruct, codellama:7b)를 같은 10문제 × 2회 프로토콜로 비교한 결과, **qwen2.5-coder:7b(Q4_K_M)를 상대적으로 가장 적합한 로컬 후보로 선정**합니다. 다만 절대 정확도는 30%(6/20)로 낮아 **첫 답변을 그대로 신뢰하는 실무 도입은 불가**하며, 사람 검토 또는 Cloud 보완을 전제로만 사용할 수 있습니다. Cloud(gpt-5.6-luna)는 같은 문제를 20/20 해결했지만 이는 로컬 선정과 별개의 운영 판단입니다.

## 1. 문제 정의와 요구사항 (실험 전 확정)

- **Use Case:** 향후 코딩 에이전트에 사용할 로컬 LLM의 기초 Python 코드 수정 능력 비교 (개발자 Coding Assistant)
- **사용자:** 팀 개발자. 입력은 `prompt.md + starter.py + test_public.py`, 출력은 python 코드 블록 1개
- **우선순위:** 정확성(전체 테스트 통과) > 응답 시간 > VRAM 사용량. 한국어 품질은 코드 생성 과제라 평가 대상에서 제외
- **환경:** Windows 11 노트북, NVIDIA RTX 5060 Laptop GPU 8,151 MiB, RAM 33.8 GB, Ollama, Python 3.12.13, pytest 8.3.5

| 필수 통과 조건 | 확인 방법 | 결과 |
|---|---|---|
| 8 GB VRAM 노트북에서 실행 가능 | `ollama ps`의 `size_vram`, 호출 성공 수 | 3개 모두 호출 성공. 단 deepseek·codellama는 VRAM 초과분이 CPU로 오프로드됨(아래 3절) |
| 상업적 사용 가능 License | Model Card / Ollama license 원문 | qwen Apache-2.0, deepseek DeepSeek Model License(상업 허용 명시), codellama Llama 2 Community License(MAU 7억 초과 조건) |
| 입력 8,192 토큰·출력 2,048 토큰 수용 | 문서상 최대 컨텍스트 vs 실험 `num_ctx` | 3개 모두 충족(32K / 16K / 16K ≥ 8K) |
| 최소 품질: 응답이 python 코드 블록 1개로 추출 가능 | 형식 오류 건수 | qwen·deepseek 0건, codellama 5/20건 형식 위반 |

선호 우선순위(필수 조건 충족 후): ① 완전 해결 횟수/20 ② 두 번 모두 해결한 문제 수/10 ③ 평균 응답 시간 ④ VRAM. 판정 기준·문제·테스트·추출 규칙은 실험 전 커밋(`57f9bc8`)에서 고정했습니다.

## 2. 환경

- 실험 commit SHA: 로컬 공식 실행 `57f9bc8`(chanyeongg3, `source_dirty: False`) / Cloud 실행 `d339b0c`(`source_dirty: True`, 이유는 8절)
- 실행 날짜·실행자: 2026-09-15 chanyeongg3(qwen, deepseek), 2026-09-15 김지수(qwen, deepseek), 2026-09-16 errorn(codellama, Cloud), 2026-09-16 김지수(Cloud)
- Windows 11 / Python 3.12.13 / pytest 8.3.5 / uv(`uv.lock` 고정) / Ollama 0.34.1 (참가자 3명 동일, 팀 확인값. manifest에는 미기록)
- CPU 24 logical / GPU NVIDIA GeForce RTX 5060 Laptop 8,151 MiB / RAM 33.8 GB. 참가자 3명 모두 동일 사양의 **서로 다른 노트북**
- Python 평가기: `python-subprocess`, runner hash `3e35801a…`, wall timeout 30 s
- 고정 옵션: `num_ctx 8192`, `num_predict 2048`, `temperature 0.2`, seed 42/43, 재시도 없음, 대화 이력 리셋
- 실행 순서: 모델 → 문제 → 반복. 모델당 워밍업 1회는 집계에서 제외(`model-1/warmup.raw.json`)

## 3. 모델 후보

| 항목 | Local A | Local B | Local C (탐색) | Cloud |
|---|---|---|---|---|
| 전체 태그·모델 ID | `qwen2.5-coder:7b-instruct` (= `qwen2.5-coder:7b`) | `deepseek-coder:6.7b-instruct` | `codellama:7b` | `gpt-5.6-luna` |
| digest / 원본 모델 | `dae161e2…f4364` / Qwen2.5-Coder-7B-Instruct | `ce298d98…dc13` / deepseek-coder-6.7b-instruct | 미기록(`runs/` 미커밋) / CodeLlama-7B | OpenAI 정식 모델 스냅샷 `gpt-5.6-luna` (GPT-5.6 계열, 비용 최적화 티어) |
| 파라미터 / 양자화 | 7.6B / Q4_K_M | 7B / Q4_0 | 7B / Q4_0 | 미공개 (문서상 GPT-5 nano 티어 상당) |
| 아키텍처 | qwen2 (GQA) | llama (MHA) | llama2 (MHA) | 미공개, 추론 토큰 지원 |
| Model Card / License URL | https://ollama.com/library/qwen2.5-coder (Apache-2.0 원문 포함) | https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct (DeepSeek Model License, 코드 MIT) | https://ollama.com/library/codellama (Llama 2 Community License) | https://developers.openai.com/api/docs/models/gpt-5.6-luna (OpenAI API 이용약관, 가중치 비공개) |
| 라이선스 적합성 | 상업 사용 가능 | 상업 사용 허용 명시, `LICENSE-MODEL` 세부 제한 확인 필요 | MAU 7억 초과 기업 별도 조건 | API 이용약관 범위 내 상업 사용 가능, 자체 호스팅 불가 |
| 문서상 최대 컨텍스트 / 실험 설정 | 32,768 / 8,192 | 16,384 / 8,192 | 16,384 / 8,192 | 1,050,000 (최대 출력 128,000) / 출력 한도 2,048 |
| 다운로드 크기 / 로드 크기(`ollama ps` size) / VRAM(`size_vram`) | 미기록 / 4,987 MB / 4,756 MiB (100% GPU) | 미기록 / 8,324 MB / 5,943 MiB (**약 25% CPU 오프로드**) | 미기록 / 8,322 MB / 6,230 MiB (**약 25% CPU 오프로드**) | 해당 없음 |
| 후보 선정 이유 | 코드 특화, 8 GB VRAM에 적재 가능, Apache-2.0 | 코드 특화, 비슷한 크기의 대조군 | Llama2 계열 코드 모델 대조군 | 수업 선행 가이드(`02_luna_chat.py`)에서 지정한 Cloud 기준선 |

로드 크기가 VRAM을 넘는 deepseek·codellama는 매 토큰마다 CPU↔GPU 전송이 일어나 속도가 절반 이하로 떨어졌습니다. 이는 KV 캐시가 큰 MHA 구조와 구형 Q4_0 양자화의 영향이며, 서로 다른 모델의 차이를 양자화만의 효과로 해석하지 않습니다.

## 4. 전체 로컬 비교 (10문제 × 2회 = 모델당 20회)

세 참가자 모두 같은 사양의 다른 노트북에서 실행했으므로 **정확도(해결 수)는 합쳐 비교하되, 속도·VRAM은 같은 PC 안에서만 상대 비교**합니다.

| 지표 | qwen2.5-coder:7b | deepseek-coder:6.7b | codellama:7b (탐색) |
|---|---|---|---|
| 호출 성공 / 계획 20회 | 20/20 | 20/20 | 19/20 (인프라 오류 1) |
| **완전 해결 / 계획 20회** | **6/20 (30%)** | 2/20 (10%) | 1/20 (5%) |
| 두 번 모두 해결 / 10문제 | 3/10 (B02·B04·B06) | 1/10 (B06) | 0/10 |
| 성공 응답 중 완전 해결 / n | 6/20 | 2/20 | 1/19 |
| 형식(추출) 오류 | 0 | 0 | 5 (완화 규칙 기준) |
| 전체 응답 시간 평균 (n) | 2.225 s (n=20) | 7.710 s (n=20) | 17.08 s (n=19) |
| 로딩 시간 평균 (n) | 0.002 s (n=20) | 0.002 s (n=20) | 미기록 |
| 생성 tokens/s 평균 (n) | 66.23 (n=20) | 28.21 (n=20) | 30.25 (n=19) |
| VRAM MiB 평균 (n) | 4,756 (n=20) | 5,943 (n=20) | 6,230 (n=19) |
| 근거 폴더 | `results/chanyeongg3/20260915-qwen25-coder-7b/` | `results/chanyeongg3/20260915-deepseek-coder-67b/` | `docs/EXPLORATORY_REPORT_qwen_vs_codellama.md` (원본 `runs/` 미커밋) |

**교차 재현:** 김지수가 별도 노트북에서 실행한 qwen/deepseek(`results/김지수/no-docker-exploratory-20260915T041139Z/`)는 문제별 해결 패턴·출력 토큰 수·VRAM이 chanyeongg3 결과와 완전히 일치했고(qwen 6/20, deepseek 2/20), tokens/s만 60.78 vs 66.23으로 장비 차이만큼 달랐습니다. seed 고정 조건에서 같은 GPU 계열이 결정적으로 재현된다는 근거로, 해결 수 비교의 신뢰도를 높입니다.

| 문제 | qwen 1회 | qwen 2회 | deepseek 1회 | deepseek 2회 | 대표 실패 근거 |
|---|---|---|---|---|---|
| B01 금액 반올림 | 실패 | 실패 | 실패 | 실패 | qwen: 합계를 한 번만 반올림(`test_no_rounding_carry_between_lines`). deepseek: 코드가 중간에 끊겨 `SyntaxError` |
| B02 페이지네이션 | 해결 | 해결 | 실패 | 실패 | deepseek: 반환 키 오타 `pageage_size` |
| B03 선택 입력 검증 | 실패 | 실패 | 실패 | 실패 | qwen: `DID NOT RAISE ValueError` (거부 분기 누락) |
| B04 시간 범위 | 해결 | 해결 | 실패 | 실패 | |
| B05 요청 멱등성 | 실패 | 실패 | 실패 | 실패 | qwen: 입력 변형·반환값 공유 |
| B06 사용자별 캐시 | 해결 | 해결 | 해결 | 해결 | 두 모델 모두 통과한 유일한 문제 |
| B07 부분 업데이트 | 실패 | 실패 | 실패 | 실패 | qwen: 누락/null/falsy 구분 실패 (공개 테스트도 실패) |
| B08 재시도·부작용 | 실패 | 실패 | 실패 | 실패 | qwen: 부작용 중복, 오류 분류 누락 |
| B09 객체 접근 권한 | 실패 | 실패 | 실패 | 실패 | qwen: 거부 시 상태 미유지 (1개 테스트만 실패) |
| B10 주문·재고 원자성 | 실패 | 실패 | 실패 | 실패 | qwen: 롤백 실패 |

상태는 `solved` / `test_failure` / 형식 오류 / 호출 실패 / 인프라 오류로 구분했고 모든 실행이 완료됐습니다(not_run 0). codellama는 원본 `runs/`가 커밋되지 않아 문제별 상태를 표에 넣지 않았고(1/20 해결, 어느 문제인지 문서에 미기록), 합계 수치만 4절 표에 인용합니다.

**실패 원인 분류(qwen 기준):** 알고리즘 난이도가 아니라 명세의 암묵적 계약 위반입니다. ① 검증·예외 분기 누락(B03·B08·B09), ② 입력 불변성·반환값 독립성 위반(B01·B05), ③ 다단계 상태 롤백 실패(B08·B10). 대부분 공개 테스트는 통과하고 숨김 테스트에서만 깨졌으며(B07 예외), 반복 간 결과가 흔들린 문제는 0건이라 표본 운이 아닌 재현되는 실패입니다. 원인은 모델 쪽이며, 프롬프트·환경·측정 문제는 아닙니다(형식 오류·타임아웃·인프라 오류 0건, `done_reason=stop`).

## 5. 같은 5문제의 Local–Cloud 비교

발제문 STEP 7과 [CLOUD.md](CLOUD.md)에 따라 사전 지정 5문제 **B01·B04·B06·B08·B10**을 비교합니다. Local은 각 10회(5×2), Cloud는 5회(5×1)입니다. Cloud 5회는 errorn이 실행한 20회(10×2, `results/cloud/20260916-gpt5-6-luna/`) 중 해당 5문제의 **1회차를 사후 추출**한 값이며, 5문제는 결과 확인 전에 `CLOUD.md`에서 고정된 세트입니다.

| 지표 | qwen2.5-coder:7b (Local) | deepseek-coder:6.7b (Local) | gpt-5.6-luna (Cloud) |
|---|---|---|---|
| 동일 5문제 해결 비율 (n) | 4/10 (B04·B06 각 2회) | 2/10 (B06 2회) | **5/5** |
| 응답 시간 평균 (n) | 2.453 s (n=10, 로컬 GPU) | 8.458 s (n=10, 로컬 GPU) | 7.263 s (n=5, 네트워크 포함) |
| 입력 / 출력 토큰 | 미집계 / 1,469 | 미집계 / 1,960 | 4,491 / 2,399 (추론 토큰 1,529 포함) |
| 추정 비용 (5회) | 장비·전력 외 추가 비용 없음 | 동일 | **약 $0.0038** (입력 4,491×$0.20/1M + 출력 2,399×$1.20/1M) |

참고로 Cloud 전체 20회는 20/20 해결, 입력 15,890 / 출력 6,567(추론 3,580) 토큰, 평균 4.85 s(n=20), 추정 비용 약 $0.0111이었습니다. 로컬은 qwen 6/20, deepseek 2/20이며 반복 수가 다르므로 분모를 함께 표시했습니다.

- **속도는 같은 축이 아닙니다.** 로컬은 GPU 추론 시간, Cloud는 네트워크 왕복 포함이라 우열 판단에 쓰지 않습니다.
- **비용:** 단가는 OpenAI 공식 가격표(https://developers.openai.com/api/docs/pricing, 2026-09-17 확인, USD, short context 기준) 입력 $0.20 / 출력 $1.20 per 1M 토큰입니다. 추론 토큰은 출력 토큰에 포함돼 과금됩니다. 5문제 1회 기준 약 $0.0038, 이번 프로젝트 전체 Cloud 호출(errorn 20회 + 김지수 20회)도 $0.03 미만입니다. 이 값은 토큰 수 × 단가의 **추정치**이며 실제 청구 내역은 OpenAI 사용량 페이지에서 별도 확인해야 합니다. 로컬 모델은 호출당 비용이 없지만 8 GB GPU 노트북(전력·관리)을 점유합니다.
- **샘플링 비대칭:** Cloud는 `temperature` 지정이 거부되어(HTTP 400) 서버 기본값(1.0 / top_p 0.98)으로, 로컬은 0.2로 실행됐습니다. 무작위성이 큰 조건에서도 Cloud가 전부 해결했으므로 이 비대칭은 Cloud에 불리한 방향이고 결론을 바꾸지 않습니다. Cloud는 seed가 없어 반복 재현이 불가능합니다.
- **보안·운영:** 로컬은 코드가 장비 밖으로 나가지 않고 비용이 0이지만 8 GB VRAM 노트북 관리가 필요합니다. Cloud는 코드가 외부로 전송되고 호출당 과금·네트워크 의존이 있으나 인프라 부담이 없습니다.
- **커스터마이징:** 로컬은 모델 교체·양자화·내부망 구성이 가능하고, Cloud는 제공 모델과 API 범위에 종속됩니다.

## 6. 최종 선정

- **필수 통과 조건과 최소 품질(사전 확정):** 8 GB VRAM 실행 가능, 상업적 사용 가능 License, 8,192/2,048 토큰 수용, python 코드 블록 1개로 추출 가능
- **상대적으로 적합한 로컬 모델:** **qwen2.5-coder:7b (Q4_K_M)**. 근거: 완전 해결 6/20으로 다른 두 후보(2/20, 1/20)의 3배 이상, 두 번 모두 해결 3/10, 형식 오류 0, 응답 시간 2.2 s로 가장 빠르고 VRAM 4,756 MiB로 유일하게 100% GPU 상주, Apache-2.0
- **탈락 후보의 구체적 실패 사례:** deepseek-coder는 B01에서 코드가 중간에 끊겨 `SyntaxError`(출력 한도와 무관, `eval_count` 109), B02에서 반환 키 오타로 실패. codellama는 20회 중 5회가 코드 블록 형식 위반, 나머지도 1회만 해결. 두 모델 모두 VRAM 초과로 CPU 오프로드가 발생해 응답이 3~7배 느림
- **실제 도입 가능 여부:** **불가(단독 사용 기준).** 상대적 승자인 qwen도 30% 정확도이며 상태 관리·예외 경로가 얽힌 7문제를 2회 모두 실패했습니다. 첫 답변을 사람이 검토하거나 테스트로 걸러내는 워크플로우에서만 보조 도구로 쓸 수 있습니다
- **Cloud 사용 권고:** 계약 예외 조항이 많은 작업(불변성·오류 분류·롤백)은 Cloud(20/20, 문제당 약 $0.001)로 보완하는 하이브리드 운영을 권고합니다. 비용보다는 코드의 외부 전송 허용 여부가 실제 제약이므로, 외부 전송이 허용되는 저장소에 한해 사용하고 호출당 토큰 상한(`max_output_tokens`)을 고정합니다
- **한계:** 10문제 × 2회는 통계적 우위를 선언하기에 작은 표본입니다. 결과는 RTX 5060 Laptop 8 GB, Q4 양자화, `num_ctx 8192`, `temperature 0.2` 조건에 한정됩니다. 세 참가자의 노트북이 같은 사양이지만 물리적으로 다른 장비이므로 속도 절대값을 합산하지 않았습니다. Cloud는 sampling·seed를 통제하지 못했고 단일 실행이며, 비용은 청구서가 아닌 토큰 기반 추정치입니다. codellama는 원본 로그가 저장소에 없고 완화된 추출 규칙으로 채점됐습니다
- **후속 실험(본 비교와 분리):** ① Cloud를 `temperature 0.2`로 재실행해 비대칭 제거 ② qwen2.5-coder 14B 또는 Q8 양자화 비교(도전 실습 A) ③ codellama를 공식 `run-model`로 재실행해 원본 로그 확보 ④ 실패 7문제에 대한 few-shot 프롬프트 개선 효과 측정

## 7. 참여 기록

[EXPERIMENT.md](EXPERIMENT.md)의 참여 기록 표와 README의 팀원별 기여를 참고하세요. 모든 팀원이 모델 실행·결과 기록·해석에 참여했고, 문제·테스트·하네스를 만든 김창동과 별개로 chanyeongg3·김지수가 채점 결과를 독립 재현했습니다.

## 8. 채점 규칙 변경 이력 (투명성)

- `57f9bc8`(공식 로컬 실행 시점): 코드 추출 규칙은 "` ```python ` 펜스 정확히 1개, 앞뒤 텍스트 없음"
- `e97e8a2`(2026-09-16 병합, errorn): codellama가 매번 설명 문장을 붙여 19/20이 추출 실패하는 문제로 `python`/`py`/무라벨 펜스 허용, 앞뒤 설명 텍스트 무시로 완화. `tests/test_core.py` 갱신, 전체 테스트 통과
- 영향: qwen·deepseek·Cloud는 모두 fenced 블록 1개만 반환해 규칙 변경과 무관(김지수·chanyeongg3 결과가 문제별로 완전 일치함으로 확인). codellama 수치만 완화 규칙 기준
- Cloud manifest의 `source_dirty: True`는 실행 스크립트 `scripts/cloud_run_model.py`가 당시 미커밋 신규 파일이었기 때문이며 채점 로직 변경은 없었습니다

## 9. 보안 점검

`results/` 전체에서 API 키·Authorization 헤더·자격증명 패턴은 탐지되지 않았습니다. 프롬프트에는 공개 벤치마크 코드만 포함됩니다. `model-1/show.raw.json`의 Modelfile 경로와 일부 pytest 로그에 `C:\Users\<사용자명>\` 형태의 Windows 사용자명이 남아 있으며, 팀 합의로 마스킹 없이 공개합니다.
