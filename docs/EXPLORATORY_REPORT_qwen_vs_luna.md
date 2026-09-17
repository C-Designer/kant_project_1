# 탐색 실행 보고서: qwen2.5-coder:7b vs gpt-5.6-luna

> **정정 주석 (2026-09-17, 병합 시 추가):** 아래 경고문의 "Docker 격리 없이 실행해 비공식"이라는 표현은 작성 시점 기준입니다. Docker 기반 평가기는 커밋 `e069b94`("Run benchmark evaluation directly in Python and simplify setup")에서 제거됐고, 현재 공식 평가기는 이 실행과 동일한 `python-subprocess` 방식입니다. 따라서 **이 보고서의 채점 방식은 현재 공식 절차와 같으며**, chanyeongg3의 공식 `run-model` 결과와 문제별 해결 패턴이 완전히 일치해 교차 재현 근거로 사용합니다. 원문은 작성자 기록 보존을 위해 수정하지 않았습니다.

> ⚠️ **비공식 결과입니다.** 이 장비에는 Docker Desktop/WSL2가 설치되어 있지 않아, 프로젝트가 요구하는
> 컨테이너 격리(`harness/docker_runner.py`, 네트워크·자원 제한) 없이 생성 코드를 호스트 서브프로세스에서
> 직접 실행해 채점했습니다. Prompt 생성·코드 추출·pytest 판정 로직 자체는 공식 harness와 동일하게
> `harness.core` / `harness.evaluator`를 그대로 재사용했지만, 격리 없이 실행한 결과이므로 팀의 공식
> 비교로 제출하기 전에 Docker 환경에서 재검증이 필요합니다. 원본 응답·solution.py·pytest 로그 전체는
> 로컬의 `runs/luna-002/`에 남아 있으며, `runs/`는 `.gitignore` 대상이라 이 저장소에는 커밋하지 않았습니다.

로컬 2종(qwen2.5-coder vs deepseek-coder) 비교는 별도 실험이며
[EXPLORATORY_REPORT_qwen_vs_deepseek.md](EXPLORATORY_REPORT_qwen_vs_deepseek.md)에 있습니다. 그 실험에서
qwen2.5-coder:7b가 deepseek-coder:6.7b-instruct를 앞섰기 때문에(6/20 대 2/20), 이번 실험의 로컬
대표 모델로 qwen2.5-coder:7b를 사용했습니다.

## 실행 조건

두 모델 모두 같은 문제(B01–B10), 같은 프롬프트 생성기(`harness.core.build_prompt`), 같은 pytest
평가기(공개 테스트 + 숨김 테스트 전부 통과해야 `solved`)로 **각 문제 2회씩, 모델당 20회** 실행했습니다.
첫 응답만 채점하며 재시도·수정 루프는 없습니다.

| | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| 호출 경로 | Ollama `/api/generate` | OpenAI Responses API |
| 문제 × 반복 | B01–B10 × 2회 = 20회 | B01–B10 × 2회 = 20회 |
| 생성 옵션 | `num_ctx=8192`, `num_predict=2048`, `temperature=0.2` | `max_output_tokens=2048`, `reasoning.effort=none`, `tools=[]`, `store=False` |
| 실제 적용된 샘플링 | temperature 0.2 | **temperature 1.0, top_p 0.98** (서버 기본값) |
| 반복 구분 | seed 42 / 43 | seed 미지원 (독립 호출) |
| 장비 | RTX 5060 Laptop (VRAM 8GB) | 원격 API |

**설정 차이 기록 (중요):** 수업에서 제공한 `02_luna_chat.py`가 `temperature`를 지정하지 않기 때문에,
이번 20회는 서버 기본값인 **temperature 1.0 / top_p 0.98**로 실행되었습니다. 로컬은 temperature 0.2
입니다. 즉 **Cloud 쪽이 로컬보다 무작위성이 훨씬 큰 조건에서 실행**되었습니다.

확인 결과 이 엔드포인트는 `temperature`를 **지정할 수 있습니다**(0.2로 지정하면 응답에 0.2로 반영됨).
따라서 이 차이는 원리적으로 제거 가능한 비대칭이며, 공식 실행에서는 `temperature=0.2`로 맞춰
재실행하는 것이 옳습니다. 반면 `seed`는 Responses API에 존재하지 않아 반복 간 재현 고정은 불가능하며,
반복 2회는 독립 호출로 수행했습니다. 10문제 중 7문제에서 2회차 응답 텍스트가 1회차와 달라 실제로
독립 샘플링이 일어났음을 확인했습니다(나머지 3문제는 텍스트가 동일).

다만 이 비대칭은 **Luna에게 불리한 방향**입니다. 무작위성이 큰 조건(temperature 1.0)에서도 20/20을
기록했으므로, 로컬과 같은 0.2로 맞추면 결과가 나빠질 이유는 없습니다. 아래 결론은 이 점에서
보수적으로 읽어도 유지됩니다.

## 결과 요약

| 지표 | qwen2.5-coder:7b | gpt-5.6-luna |
|---|---|---|
| 완전 해결 / 계획 20회 | 6/20 (30%) | **20/20 (100%)** |
| 두 번 모두 해결 / 10문제 | 3/10 | **10/10** |
| 호출 성공 / 시도 | 20/20 | 20/20 |
| 형식 오류 (추출 실패) | 0 | 0 |
| 인프라 오류 | 0 | 0 |
| 평균 응답 시간 | 2.305s (n=20, 로컬 GPU) | 약 2.2s (n=20, 네트워크 포함) |
| 평균 생성 속도 | 60.78 tokens/s (n=20) | 측정 축 다름 (API 미제공) |
| 평균 VRAM | 4756 MiB (n=20) | 해당 없음 |
| 총 토큰 | 측정 대상 아님 | 입력 15,890 / 출력 2,990 |

## 문제별 반복 상태

| 문제 | 주제 | qwen 1회 | qwen 2회 | luna 1회 | luna 2회 |
|---|---|---|---|---|---|
| B01 | 금액 반올림 | test_failure | test_failure | **solved** | **solved** |
| B02 | 페이지네이션 | solved | solved | **solved** | **solved** |
| B03 | 선택 입력 검증 | test_failure | test_failure | **solved** | **solved** |
| B04 | 시간 범위 | solved | solved | **solved** | **solved** |
| B05 | 요청 멱등성 | test_failure | test_failure | **solved** | **solved** |
| B06 | 사용자별 캐시 | solved | solved | **solved** | **solved** |
| B07 | 부분 업데이트 | test_failure | test_failure | **solved** | **solved** |
| B08 | 재시도·부작용 | test_failure | test_failure | **solved** | **solved** |
| B09 | 객체 접근 권한 | test_failure | test_failure | **solved** | **solved** |
| B10 | 주문·재고 원자성 | test_failure | test_failure | **solved** | **solved** |

## 해석 (비공식, 팀 검증 전)

**gpt-5.6-luna는 계획된 20회를 모두 해결했고(20/20), 10문제 전부에서 두 반복 모두 성공했습니다.**
같은 조건에서 qwen2.5-coder:7b는 6/20, 두 번 모두 해결한 문제는 3/10이었습니다.

qwen2.5-coder가 두 번 모두 실패한 7문제(B01·B03·B05·B07·B08·B09·B10)를 Luna는 두 번 모두 해결했습니다.
이 7문제는 Decimal 줄별 반올림, 오류 우선순위, 멱등성 스냅샷, falsy 값 부분 업데이트, 오류 분류·중복
방지, 거부 시 상태 유지, 중간 실패 복구처럼 **계약의 예외 조항을 정확히 읽어야 하는 문제**들입니다.
로컬 7B 모델이 반복해서 놓친 지점이 바로 이 영역이고, 두 모델의 격차도 여기서 발생했습니다.

출력량도 Luna 쪽이 적었습니다. 20회 평균 출력이 150 토큰(최소 76, 최대 311)으로, 설명 없이 요구된
코드 블록만 정확히 반환해 형식 오류가 0건이었습니다.

## 한계

- **샘플링 조건 불일치:** Cloud는 temperature 1.0(서버 기본값), 로컬은 0.2로 실행되었습니다.
  `temperature`는 지정 가능하므로 공식 실행에서는 0.2로 맞춰 재실행해야 합니다. `seed`는 Responses
  API에 없어 반복 재현 고정은 어느 설정으로도 불가능하며, 두 모델의 "2회 반복"은 같은 의미가 아닙니다.
- **반복 간 동일 응답:** Luna는 10문제 중 3문제에서 2회차 응답이 1회차와 텍스트까지 동일했습니다.
  해당 문제의 두 반복은 독립 표본으로 보기 어렵습니다.
- **속도 비교 불가:** 로컬은 GPU 생성 시간, Cloud는 네트워크 왕복을 포함한 시간이며 장비가 다릅니다.
  같은 축에서 비교하지 마세요.
- **표본 크기:** 10문제·2반복은 통계적 우열을 단정하기에 작습니다
  ([EXPERIMENT.md](EXPERIMENT.md) 참고). 다만 20/20 대 6/20은 표본 오차로 설명하기 어려운 격차입니다.
- **격리 없음:** Docker 격리 없이 호스트에서 채점했습니다.
- **비용:** Cloud 호출 비용은 별도이며 이 보고서에 포함하지 않았습니다. 로컬 실행은 추가 비용이 없습니다.

## 운영 권고

로컬 모델 선정과 Cloud 사용 판단은 별개 결론입니다.

- **정확도만 보면 gpt-5.6-luna가 압도적**입니다(20/20 대 6/20). 계약 예외 조항이 많은 과제에서는
  로컬 7B 모델을 단독으로 쓰기 어렵다는 근거가 됩니다.
- 대신 Cloud는 호출당 비용·네트워크 의존·코드의 외부 전송이라는 조건이 붙습니다. 로컬 모델은
  비용이 없고 코드가 장비 밖으로 나가지 않습니다.
- 로컬 모델을 쓸 경우 첫 응답을 그대로 신뢰하지 말고 사람의 검토를 전제해야 합니다.

## 재현 방법

```powershell
# Cloud 20회 호출 (반복 1, 2). 키는 .env의 OPENAI_API_KEY에서 읽으며 출력되지 않음
uv run python scripts/luna_ten_cases.py 1
uv run python scripts/luna_ten_cases.py 2
```

채점 결과·자동 보고서·원본 응답·solution.py·pytest 로그는
`results/김지수/luna-exploratory-20260916T080707Z/`에 커밋되어 있습니다.
로컬 결과는 `results/김지수/no-docker-exploratory-20260915T041139Z/REPORT.md`에 있습니다.

`temperature`를 로컬과 맞춰 재실행하려면 `scripts/luna_ten_cases.py`의
`client.responses.create(...)` 호출에 `temperature=0.2`를 추가하세요.
