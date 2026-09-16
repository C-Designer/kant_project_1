# 탐색 실행 보고서: qwen2.5-coder:7b vs deepseek-coder:6.7b-instruct

> ⚠️ **비공식 결과입니다.** 이 장비에는 Docker Desktop/WSL2가 설치되어 있지 않아, 프로젝트가 요구하는
> 컨테이너 격리(`harness/docker_runner.py`, 네트워크·자원 제한) 없이 생성 코드를 호스트 서브프로세스에서
> 직접 실행해 채점했습니다. Prompt 생성·코드 추출·pytest 판정 로직 자체는 공식 harness와 동일하게
> `harness.core` / `harness.ollama` / `harness.evaluator.parse_report`를 그대로 재사용했지만, 격리 없이
> 실행한 결과이므로 팀의 공식 비교(`results/<participant>/<run-id>`, Docker 검증 필수)로 제출하기 전에
> Docker 환경에서 재검증이 필요합니다. 원본 로그·응답·solution.py·pytest 로그 전체는 로컬의
> `runs/no-docker-exploratory-20260915T041139Z/`에 남아 있으며, `runs/`는 `.gitignore` 대상이라 이
> 저장소에는 커밋하지 않았습니다.

## 실행 조건
- 문제: B01–B10 (harness 기본 10문제), 각 문제 2회 반복 (seed 42, 43)
- 옵션: `num_ctx=8192`, `num_predict=2048`, `temperature=0.2`
- GPU: NVIDIA GeForce RTX 5060 Laptop (VRAM 8GB)
- 채점: harness와 동일한 pytest 판정 로직, 컨테이너 대신 호스트 서브프로세스 실행 (자원/네트워크 격리 없음)

## 결과 요약

| 지표 | qwen2.5-coder:7b | deepseek-coder:6.7b-instruct |
|---|---|---|
| 완전 해결 / 계획 20회 | 6/20 | 2/20 |
| 두 번 모두 해결 / 10문제 | 3/10 | 1/10 |
| 호출 성공 / 시도 | 20/20 | 20/20 |
| 인프라 오류 | 0 | 0 |
| 평균 응답 시간 (n=20) | 2.305s | 7.699s |
| 평균 로딩 시간 (n=20) | 0.003s | 0.003s |
| 평균 생성 속도 (n=20) | 60.78 tokens/s | 28.08 tokens/s |
| 평균 VRAM (n=20) | 4756 MiB | 5943 MiB |

## 문제별 반복 상태 (해결 / 테스트 실패)

| 문제 | qwen2.5-coder 1회 | qwen2.5-coder 2회 | deepseek-coder 1회 | deepseek-coder 2회 |
|---|---|---|---|---|
| B01 | test_failure | test_failure | test_failure | test_failure |
| B02 | solved | solved | test_failure | test_failure |
| B03 | test_failure | test_failure | test_failure | test_failure |
| B04 | solved | solved | test_failure | test_failure |
| B05 | test_failure | test_failure | test_failure | test_failure |
| B06 | solved | solved | solved | solved |
| B07 | test_failure | test_failure | test_failure | test_failure |
| B08 | test_failure | test_failure | test_failure | test_failure |
| B09 | test_failure | test_failure | test_failure | test_failure |
| B10 | test_failure | test_failure | test_failure | test_failure |

## 해석 (비공식, 팀 검증 전)
이번 탐색 실행에서는 qwen2.5-coder:7b가 deepseek-coder:6.7b-instruct보다 정답률(30% vs 10%)과 생성
속도(약 2.6배) 모두에서 앞섰습니다. 다만 10문제·2반복만으로는 통계적 우위를 단정할 수 없고
([EXPERIMENT.md](EXPERIMENT.md) 참고), Docker 격리 없이 실행된 결과라는 한계가 있습니다. 팀의 공식
모델 선정에는 Docker 환경에서의 재실행 결과를 사용해야 합니다.
