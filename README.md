# KANT Project 1: 로컬 LLM 코딩 성능 비교

**팀원 각자가 담당 로컬 모델 하나를 20회 테스트하고, 자동 보고서와 본인 해석을 남겨 push합니다.** 팀 전체에서는 서로 다른 모델 최소 2개를 비교합니다. 에이전트·UI·Tool Calling·재수정 루프는 없으며, 첫 답변의 전체 테스트 통과만 해결로 인정합니다.

- **[팀원별 실행 → 보고서 → push 가이드](docs/INDIVIDUAL_RUN.md)**
- [팀 Notion 안내](https://app.notion.com/p/teamsparta/LLM-3dc2dc3ef514806d8b73eb017901cd17)
- [실험 규약·팀 참여 기록](docs/EXPERIMENT.md)
- [검증 상태](docs/VALIDATION.md)
- [결과·모델 선정 양식](docs/RESULTS_TEMPLATE.md)
- [Cloud API 비교 방법](docs/CLOUD.md)

## 가장 빠른 개인 실행 흐름
Windows PowerShell 예시입니다. Git·uv·Ollama이 설치되어 있어야 합니다. 모델 태그와 본인 ID는 직접 정합니다.

```powershell
git switch main
if ($LASTEXITCODE -ne 0) { throw "main 전환 실패" }
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) { throw "최신 main 반영 실패" }
$Me = "your-github-id"
$Model = "REPLACE:full-tag"
ollama pull $Model
if ($LASTEXITCODE -ne 0) { throw "모델 다운로드 실패" }
.\scripts\run-personal.ps1 -Participant $Me -Model $Model -DeviceLabel "classroom-pc-01"
```

스크립트는 환경 준비·Python 정답/버그 사전 검증 후 **모델 하나 × 10문제 × 2회**를 실행합니다. 결과는 `results/<본인ID>/<실행ID>/`에 자동 저장됩니다.

- `REPORT.md`: 숫자·문제별 결과·환경·근거를 자동 작성
- `NOTES.md`: 모델 선택 이유·실패 사례·해석·민감 정보 확인을 팀원이 작성
- 보고서 재생성: `uv run python -m harness report <개인 실행 폴더>`
- 검토 후 **본인 실행 폴더만** `git add`, commit, 최신 main 반영, push
- 스크립트는 git commit/push나 보안 정책 변경을 자동 실행하지 않음

스크립트 사용이 어려우면 [수동 CLI와 정확한 push 명령](docs/INDIVIDUAL_RUN.md)을 따릅니다. PowerShell 스크립트와 실제 Ollama 실행은 수업 장비에서 확인해야 합니다.

## 팀원이 먼저 할 일
1. 한 문제의 `prompt.md → starter.py → test_public.py`를 읽습니다.
2. 사람이 기준을 검토할 때만 `test_hidden.py`와 `reference.py`를 봅니다. 이 둘은 모델 입력에서 제외합니다.
3. Windows 수업 노트북의 GPU·VRAM·RAM, Ollama 및 Python 평가기 작동을 확인합니다.
4. Python 평가기로 정답은 모두 통과하고 초기 코드에서는 버그가 잡히는지 확인합니다.
5. 팀에서 서로 다른 모델을 배정하고, 각자는 담당 모델의 Model Card·License·전체 태그를 기록합니다. 모두 같은 문제·생성 설정을 사용합니다. 공정한 속도 비교와 발제문 기본 요건을 위해 공통 평가 PC에서 각자 실행하는 방식을 권장합니다.

**아직 모델 성능 결과는 없습니다.** 노트북 사양·모델 후보·실장비 실행·팀 역할은 확인해야 합니다. 2060 계열 GPU는 사용자 기억이며 확정 사양이 아닙니다.

## 10문제: 실제 코드와 테스트
| ID | 주제 | 핵심 검증 | 코드 |
|---|---|---|---|
| B01 | 금액 반올림 | Decimal·항목별 HALF_UP | [보기](cases/B01) |
| B02 | 페이지네이션 | 1-based·빈 목록·범위 밖 | [보기](cases/B02) |
| B03 | 선택 입력 검증 | None 기본값·bool/int·오류 우선순위 | [보기](cases/B03) |
| B04 | 시간 범위 | aware datetime·절대 시각·반열린 구간 | [보기](cases/B04) |
| B05 | 요청 멱등성 | 동일 요청·충돌·스냅샷 | [보기](cases/B05) |
| B06 | 사용자별 캐시 | 사용자 격리·반환값 독립성 | [보기](cases/B06) |
| B07 | 부분 업데이트 | 누락/null/falsy·검증 후 반영 | [보기](cases/B07) |
| B08 | 재시도·부작용 | 오류 분류·횟수 제한·중복 방지 | [보기](cases/B08) |
| B09 | 객체 접근 권한 | 소유자·관리자·거부 시 상태 | [보기](cases/B09) |
| B10 | 주문·재고 원자성 | 중간 실패 복구·정상 처리 | [보기](cases/B10) |

각 폴더에는 `prompt.md`, `starter.py`, `reference.py`, `test_public.py`, `test_hidden.py`가 있습니다. 정확한 API·허용 입력·오류·변경 규칙은 **각 prompt.md가 기준**입니다. 이전 Notion 한 줄 후보나 대화의 예시 함수와 세부 API가 다를 수 있습니다. 난이도는 설계상 구분이지 실측 결과가 아닙니다.

## 설치 및 사전 검증
저장소 루트의 Windows PowerShell 명령입니다. Git·uv·Ollama이 필요합니다. 설치는 팀 장비 정책에 맞게 진행합니다.

```powershell
git clone https://github.com/C-Designer/kant_project_1.git
cd kant_project_1
uv sync --frozen
uv run python --version
uv run python -m pytest tests -q
uv run python -m harness verify-cases --out runs/verify-001
```

`runs/verify-001/verification_summary.json`의 `all_valid`가 true여야 합니다. 정답 10개가 모든 테스트를 통과하고 초기 코드 10개에서 평가 테스트 최소 1개가 실패해야 합니다. 평가기 실행 오류를 모델 오답으로 해석하지 마세요.

## 선택: 한 사람이 두 모델을 연속 실행하는 기존 방식
같은 PC에서 모델을 하나씩 실행합니다. 다른 모델이나 무거운 작업은 먼저 종료하고 모델 다운로드를 완료하세요. 아래 태그는 **교체용 자리표시자이지 추천 모델이 아닙니다.**

```powershell
$ModelA = "REPLACE_A:full-tag"
$ModelB = "REPLACE_B:full-tag"
ollama pull $ModelA
ollama pull $ModelB
uv run python -m harness run --models $ModelA $ModelB --out runs/local-001 --num-ctx 8192 --num-predict 2048 --temperature 0.2 --seed 42
uv run python -m harness summarize runs/local-001
```

8192/2048 등은 기본값이지 모든 장비에 검증된 값이 아닙니다. 본 실험 전에 입력 길이·장비에 맞게 고정하고 두 후보에 동일 적용합니다. 동일 기반 모델의 양자화만 다른 두 태그는 필수 요건을 충족하지 않습니다.

실행 순서는 모델 → 문제 → 반복입니다. 모델당 워밍업 1회는 별도 기록하며 해당 모델 종료 후 unload합니다. 반복 seed는 42/43으로 동일 반복에 같은 seed를 적용합니다. 서로 다른 모델의 확률적 조건이 완전히 같다는 보장은 아닙니다.

응답은 정확히 하나의 python 코드 블록이어야 합니다. 추출 실패는 형식 오류로 기록하고 수작업 보정하지 않습니다. 평가기는 생성 코드를 현재 Python의 별도 프로세스로 실행합니다.

## 결과 파일
- `manifest.json`: 계획 실행 수·문제/프롬프트 해시·설정
- `results.jsonl`: 실행별 상태·측정치·테스트 결과
- `model-*/...raw.json`: Ollama 원본 응답
- `*.solution.py`: 추출 코드. 호스트 실행 금지
- `*.pytest.log`: 테스트 근거
- `summary.json`: 모델별 집계

개인 `run-model`은 `results/<participant>/<run-id>/`에 보고서·원본·로그를 함께 만들며 **Git 추적 대상**입니다. 검토 후 그 실행 폴더만 커밋하면 됩니다. 기존 `run --out runs/...` 및 사전 검증의 `runs/`는 계속 gitignore 대상이며, 이 방식의 제출 결과만 별도 results 폴더로 복사해야 합니다.

출력은 새 디렉터리만 허용합니다. 중단된 실행도 보고서에서 미완료로 구분하고 완전한 실행과 섞지 마세요. API 키·민감 정보·모델 가중치·가상환경은 커밋하지 않습니다.

## 비교 기준
- **주 지표:** 완전 해결 횟수 / 계획 20회(모델별)
- **보조:** 두 번 모두 해결한 문제 수 / 10, 호출 성공/시도, 실패 유형
- **성능:** 응답 시간·로딩 시간·tokens/s·VRAM 및 각 n
- **Cloud:** 사전 지정 5문제 각 1회. 동일 5문제의 로컬 두 반복 모두 비교

전체 테스트를 통과해야 해결입니다. 부분 통과는 진단 정보이며 테스트 개수로 문제 가중치를 달리하지 않습니다. 호출 실패·인프라 실패·미실행은 구분하고 작은 차이를 과장하지 않습니다.

## 보안과 공유
생성 코드는 현재 사용자 권한으로 실행되며 파일과 네트워크에 접근할 수 있습니다. 임시 폴더·별도 Python 프로세스·시간 제한은 보안 격리가 아닙니다. 민감 파일 없는 실습 장비에서 실행하고, 모델 응답이 테스트 실행을 조작할 수 있다는 한계도 고려하세요.

저장소는 현재 **Private**입니다. 404가 보이는 팀원은 소유자와 협업자 초대·수락 상태를 확인하세요. 이번 작업에서는 공개 전환이나 협업자 권한 변경을 하지 않았습니다. Notion은 기존 공유 범위를 유지합니다.