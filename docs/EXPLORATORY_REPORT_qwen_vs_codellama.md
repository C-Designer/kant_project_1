# 탐색 실행 보고서: qwen2.5-coder:7b vs codellama:7b

> ⚠️ **비공식 결과입니다.** 이 실행은 두 가지 지점에서 팀 공식 절차와 다릅니다.
>
> 1. **실행 방식**: `run-model`(참가자 1명·모델 1개·20회, `results/<participant>/<run-id>` 산출)이 아니라
>    `run`(모델 2개를 한 실행에서 나란히 비교, `runs/` 산출) 명령을 사용했습니다. 원본 로그는 로컬의
>    `runs/local-001/`(수정 전 추출 규칙), `runs/local-002/`(아래 수정된 추출 규칙)에 있으며, `runs/`는
>    `.gitignore` 대상이라 이 저장소에는 커밋하지 않았습니다.
> 2. **`harness/core.py`의 `extract_python` 수정**: 팀 공식 규칙은 "여는 펜스가 정확히 ` ```python `,
>    닫는 펜스 앞뒤에 어떤 텍스트도 없어야 함"이었습니다. codellama:7b가 매 응답마다 코드 앞뒤에 설명
>    문장을 붙이는 습관 때문에 20회 중 19회가 이 규칙에서 추출 실패로 처리되어, 실제 코드 품질을 전혀
>    평가할 수 없었습니다. 이 브랜치의 `extract_python`은 **① `python`/`py`/무라벨 펜스를 모두 허용,
>    ② 펜스 앞뒤 설명 텍스트를 무시**하도록 완화했습니다("정확히 하나의 코드 블록만 허용"은 유지).
>    `tests/test_core.py`도 이에 맞춰 갱신했고 전체 테스트(185 passed, 4 skipped)가 통과합니다.
>
> 즉 이 보고서의 수치는 **팀의 공식 harness 코드와 다른 코드로 채점된 결과**이며, 그대로 팀의 공식 모델
> 선정 비교(`results/<participant>/<run-id>`)에 합산해서는 안 됩니다. 다만 아래 qwen2.5-coder:7b 수치는
> 원본(수정 전) 규칙으로 돌린 `runs/local-001`과도, chanyeongg3의 공식 제출
> (`results/chanyeongg3/20260915-qwen25-coder-7b/`)과도 거의 동일해 재현성을 교차 확인했습니다.

## 실행 조건
- 문제: B01–B10 (harness 기본 10문제), 각 문제 2회 반복 (seed 42, 43)
- 옵션: `num_ctx=8192`, `num_predict=2048`, `temperature=0.2`
- GPU: NVIDIA GeForce RTX 5060 Laptop (VRAM 8,151 MiB)
- 채점: `harness run --models qwen2.5-coder:7b codellama:7b`, 수정된 `extract_python` 사용

## 10개 기준 비교

| # | 기준 | qwen2.5-coder:7b | codellama:7b |
|---|---|---|---|
| 1 | 완전 해결 (solved/20) | **6/20 (30%)** | 1/20 (5%) |
| 2 | 두 번 모두 해결한 문제 (10문제 중) | **3/10** (B02, B04, B06) | 0/10 |
| 3 | 호출 성공률 (call_successes/attempts) | 20/20 (100%) | 19/20 (95%, 인프라 오류 1건) |
| 4 | 형식(추출) 준수율 — 완화된 규칙 기준 | 20/20 (100%) | 14/20 (70%, 추출실패 5건 + 인프라 1건) |
| 5 | 평균 응답 속도 | **61.96 tok/s** | 30.25 tok/s (약 2배 느림) |
| 6 | 평균 응답 시간 (성공 호출만) | **2.42초** | 17.08초 (약 7배 느림) |
| 7 | VRAM 사용량 / GPU 오프로딩 | 4,756 MiB, size==size_vram → **100% GPU 상주** | 실제 필요 총 8,322 MiB 중 6,230 MiB만 VRAM 상주 → **약 25%가 CPU로 오프로드** |
| 8 | 모델 아키텍처 | Qwen2, 7.6B, GQA, Q4_K_M, 학습 컨텍스트 32K | Llama2, 7B, MHA(GQA 미적용), Q4_0(구형 양자화), 학습 컨텍스트 16K |
| 9 | 라이선스 | Apache License 2.0 | Llama 2 Community License (MAU 7억 초과 기업 등 별도 조건) |
| 10 | 종합 실전 적합성 (이 GPU·이 워크플로우 기준) | 무난히 추천 가능 | 이 8GB VRAM 노트북에는 부적합 — 느리고, 정답률 낮고, 지시 준수도 낮음 |

## chanyeongg3 공식 제출과의 교차 검증 (qwen2.5-coder만)

| 지표 | 이 실행 (runs/local-002) | chanyeongg3 공식 제출 (`results/chanyeongg3/20260915-qwen25-coder-7b`) |
|---|---|---|
| 완전 해결 | 6/20 | 6/20 |
| 두 번 모두 해결 | 3/10 (B02, B04, B06) | 3/10 (B02, B04, B06) — **문제별 패턴까지 완전 일치** |
| 평균 tokens/s | 61.96 | 66.23 |
| 평균 VRAM | 4,756 MiB | 4,756 MiB |

서로 다른 실행·시각·(참가자 기준) 장비인데도 qwen2.5-coder:7b 결과가 사실상 동일하게 재현되어, 이 harness의
측정치가 안정적임을 뒷받침합니다. codellama:7b는 아직 다른 참가자의 공식 제출이 없어 교차 검증이 안 된
상태입니다.

## codellama:7b가 낮은 이유 (원인 분석)

1. **GPU 용량 초과가 속도 저하의 직접 원인입니다.** `ollama ps` 원본에서 qwen은 `size == size_vram`
   (4.99GB 전량 GPU 상주)인 반면, codellama는 `size=8.32GB` 중 `size_vram=6.23GB`만 GPU에 있고 나머지
   ~2GB는 CPU 메모리에서 처리되고 있었습니다. 8GB급 GPU에 codellama가 완전히 안 들어가 매 토큰마다
   CPU↔GPU 전송이 발생합니다.
2. **원인의 원인**: codellama(Llama2 계열)는 GQA(Grouped-Query Attention)를 쓰지 않아 KV 캐시가 크고,
   양자화도 구형 방식(Q4_0)이라 런타임 메모리 효율이 qwen2.5-coder(Qwen2, GQA, Q4_K_M)보다 떨어집니다.
3. **정답률 저하는 속도 문제와 별개입니다.** 완화된 규칙으로 추출에 성공한 14건 중에서도 solved는 1건뿐이라,
   단순 형식 문제가 아니라 실제 코드 정확성 자체가 낮습니다.
4. **완화 후에도 남은 5건의 추출 실패**는 진짜 지시 위반이었습니다 — 정답 코드 뒤에 "사용 예시" 코드
   블록을 추가로 붙이거나(블록 2개), 정답 대신 `pytest test_public.py` 실행 명령만 펜스로 감싸거나,
   백틱 없이 "python"이라는 단어만 쓴 경우가 있었습니다.

## 해석 (비공식, 팀 검증 전)
qwen2.5-coder:7b가 정답률·속도·형식준수·GPU 적합성 전 항목에서 codellama:7b를 앞섰습니다. 다만
10문제·2반복만으로는 통계적 우위를 단정할 수 없고([EXPERIMENT.md](EXPERIMENT.md) 참고), 이 보고서는
harness 공식 코드가 아닌 완화된 추출 규칙으로 채점된 결과라는 한계가 있습니다. 팀의 공식 모델 선정에는
공식 harness 코드 그대로, `run-model`로 참가자별 20회 실행한 결과를 사용해야 합니다.
