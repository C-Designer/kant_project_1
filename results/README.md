# 팀원별 모델 성능 결과

| 폴더 | 모델 | 회수 | 해결 | 성격 |
|---|---|---|---|---|
| `chanyeongg3/20260915-qwen25-coder-7b/` | qwen2.5-coder:7b-instruct | 20 | 6/20 | 공식 `run-model` |
| `chanyeongg3/20260915-deepseek-coder-67b/` | deepseek-coder:6.7b-instruct | 20 | 2/20 | 공식 `run-model` (qwen과 같은 PC) |
| `chanyeongg3/report.md` | qwen vs gpt-5.6-luna 비교 보고서 | | | 문서 |
| `김지수/no-docker-exploratory-20260915T041139Z/` | qwen2.5-coder:7b + deepseek-coder:6.7b-instruct | 20+20 | 6/20, 2/20 | 재현 실행 (chanyeongg3과 문제별 일치) |
| `김지수/luna-exploratory-20260916T080707Z/` | gpt-5.6-luna (Responses API) | 20 | 20/20 | Cloud 탐색 |
| `cloud/20260916-gpt5-6-luna/` | gpt-5.6-luna (Chat Completions) | 20 | 20/20 | Cloud 공식 5×1은 이 중 5문제 1회차 추출 ([docs/CLOUD.md](../docs/CLOUD.md)) |

codellama:7b(1/20, errorn)는 `runs/`에만 있어 이 폴더에 없습니다. 팀 종합은 [docs/FINAL_REPORT.md](../docs/FINAL_REPORT.md)를 보세요.

이 폴더는 개인 제출 위치입니다.

`run-model --participant 본인ID --model 전체태그`가 아래 구조로 새 실행 폴더를 생성합니다.

```text
results/<participant>/<run-id>/
  REPORT.md        자동 수치·문제별 결과·환경 보고서
  NOTES.md         사람이 작성하는 사례·해석·검토
  manifest.json    실험 조건·문제 해시·장비 정보
  summary.json     집계
  results.jsonl    실행별 상태
  model-1/         원본 응답·추출 코드·테스트 로그
```

- REPORT.md와 NOTES.md 및 근거 파일을 **한 실행 폴더 단위**로 push합니다.
- 기존 결과를 덮어쓰지 않습니다. 재실행은 새 run-id입니다.
- 민감 정보·API 키가 없는지 검사하고 모델 가중치·가상환경은 올리지 않습니다.
- 평가기는 생성 코드를 현재 사용자 권한으로 실행합니다. 임시 폴더·시간 제한은 보안 격리가 아니므로 민감 파일 없는 실습 장비를 사용하세요.
- 참가자 ID·장비 라벨은 사용자가 입력한 값입니다. 서로 다른 장비의 속도를 모델 자체 성능으로 단정하지 않습니다.
- 실패·중단 결과도 상태를 명시해 남깁니다. 잘 나온 결과만 골라 본 실험인 것처럼 제출하지 않습니다.
- 개인 결과를 모은 최종 비교는 [팀 종합 양식](../docs/RESULTS_TEMPLATE.md)에 작성합니다.

실행·검토·push 명령은 [개인 실행 가이드](../docs/INDIVIDUAL_RUN.md)를 따릅니다.
