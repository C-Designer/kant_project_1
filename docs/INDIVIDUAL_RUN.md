# 팀원별 모델 테스트 → 보고서 → push

각 팀원은 **담당 모델 하나를 같은 10문제 × 2회 = 20회** 실행합니다. 워밍업 1회는 별도입니다. 자동 생성된 보고서를 확인하고 짧은 해석을 남긴 뒤 본인 폴더만 push합니다.

## 1. 팀에서 먼저 맞출 것
- 서로 다른 기반의 로컬 모델을 최소 2개 배정합니다. 같은 기반 모델의 양자화만 다른 것은 필수 2모델을 대체하지 못합니다.
- 문제·테스트·생성 옵션은 동일하게 고정합니다. 결과의 manifest.json에 기록된 suite/prompt 해시와 설정으로 확인합니다.
- 발제문 기본 비교는 **동일 PC에서 두 모델**입니다. 역할은 나누되 공통 평가 PC에서 각자 담당 모델을 실행하는 방식을 권장합니다.
- 서로 다른 PC에서 실행한 개인 결과도 기록할 수 있지만 속도·VRAM 차이를 모델 자체의 우열로 해석하지 않습니다. 공식 동일 PC 비교는 별도로 확보합니다.
- 같은 모델을 여러 팀원이 실행해도 서로 다른 실행으로 보관합니다. 공식 비교에 쓸 실행과 장비는 결과를 보기 전에 정하고, 사후에 가장 좋은 개인 결과만 고르거나 다른 장비의 반복을 하나로 합치지 않습니다.
- Cloud 5문제 × 각 1회는 팀 전체에서 한 번 수행합니다. 개인별 20회만 모았다고 과제 전체가 완료되는 것은 아닙니다.

## 2. 준비: 처음 한 번
Windows PowerShell, 저장소 루트에서 실행합니다. Git·uv·Ollama이 필요합니다. 사전 설치와 장비 정책 확인은 별도입니다.

```powershell
git switch main
if ($LASTEXITCODE -ne 0) { throw "main 전환 실패" }
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) { throw "최신 main 반영 실패" }
uv sync --frozen
if ($LASTEXITCODE -ne 0) { throw "의존성 준비 실패" }
```

Git에 미커밋 변경이나 충돌이 있으면 먼저 해결합니다. 다른 팀원의 결과나 코드를 삭제하거나 force push하지 않습니다.

## 3. 본인 모델 하나 실행
아래 값은 예시 자리표시자입니다. Participant는 소문자 영문·숫자·하이픈·밑줄로 된 본인의 고유 ID를 사용합니다. 같은 ID를 여러 팀원이 공유하지 않습니다.

```powershell
$Me = "your-github-id"
$Model = "REPLACE:full-tag"
ollama pull $Model
if ($LASTEXITCODE -ne 0) { throw "모델 다운로드 실패" }

.\scripts\run-personal.ps1 -Participant $Me -Model $Model -DeviceLabel "classroom-pc-01"
```

스크립트는 저장소 루트에서 의존성 준비 → Python 평가기로 10문제 정답/버그 사전 검증 → 개인 모델 20회 실행을 진행합니다. 설치 정책으로 스크립트 실행이 막히면 보안 정책을 자동 변경하지 말고 아래 수동 명령을 사용합니다. Python 평가기 준비 또는 사전 검증에 실패하면 본 실험을 시작하지 않습니다.

종료 시 개인 결과 경로가 표시됩니다:

```text
results/
  your-github-id/
    20260915t010203z-a1b2c3d4/
      REPORT.md          자동 성능 보고서
      NOTES.md           팀원이 작성할 해석·검토
      manifest.json      설정·문제 해시·환경·담당자
      summary.json       자동 집계
      results.jsonl      20회 실행별 상태·측정치
      model-1/           원본 응답·생성 코드·테스트 로그
```

매 실행은 새 폴더를 사용하고 기존 결과를 덮어쓰지 않습니다. 스크립트는 git commit/push를 자동 실행하지 않습니다.

### 수동 명령으로 실행하는 경우
```powershell
$Me = "your-github-id"
$Model = "REPLACE:full-tag"
$RunId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ", [System.Globalization.CultureInfo]::InvariantCulture).ToLowerInvariant() + "-" + ([guid]::NewGuid().ToString("N").Substring(0,8))
foreach ($Id in @($Me, $RunId)) {
    if ($Id -cnotmatch '^[a-z0-9][a-z0-9_-]{0,63}$' -or $Id -match '^(con|prn|aux|nul|com[1-9]|lpt[1-9])$') {
        throw "본인 ID 또는 실행 ID가 잘못되었습니다. 경로 구분자는 사용할 수 없습니다."
    }
}
$RunDir = "results/$Me/$RunId"

uv sync --frozen
if ($LASTEXITCODE -ne 0) { throw "의존성 준비 실패" }
uv run python -m harness verify-cases --out "runs/verify-$Me-$RunId"
if ($LASTEXITCODE -ne 0) { throw "사전 검증 실패: 본 실험 중단" }
uv run python -m harness run-model --participant $Me --model $Model --run-id $RunId --device-label "classroom-pc-01"
if ($LASTEXITCODE -ne 0) { throw "실행 중단: 생성된 보고서 상태 확인" }
```

기본 설정은 num_ctx=8192, num_predict=2048, temperature=0.2, seed=42/43입니다. 장비에서 검증된 보장값이 아닙니다. 바꿀 경우 팀이 본 실험 전에 같은 값으로 정하고 run-model 옵션 또는 스크립트 파라미터를 함께 변경합니다. 모델 카드·라이선스 URL은 CLI의 --model-card-url, --license-url 또는 NOTES.md에 기록합니다.

## 4. 자동 보고서를 확인하고 짧게 해석
- REPORT.md: 해결 수, 호출 성공 수, 미실행 수, 문제별 두 반복 결과, 응답/로딩 시간·tokens/s·VRAM과 표본 수 n, 환경·설정·근거 링크를 자동 작성합니다.
- NOTES.md: 모델 선택 이유와 라이선스 확인, 대표 성공/실패 사례, 결과 해석, 한계, 민감 정보 검토를 사람이 작성합니다.
- 정답 구현 테스트의 100/100과 LLM의 20회 성적은 서로 다른 값입니다.
- 20회 기록이 있다고 20회 성공한 것은 아닙니다. 호출 실패·형식 오류·테스트 실패·평가기 실행 오류를 구분하고, 중단된 결과는 미완료로 표시합니다.
- 기존 NOTES.md는 보고서를 재생성해도 덮어쓰지 않습니다.

```powershell
# 실제 표시된 경로로 교체합니다.
$RunDir = "results/your-github-id/실제-run-id"
notepad "$RunDir/NOTES.md"

# 필요할 때 숫자 보고서 재생성. 모델/테스트 재실행은 하지 않습니다.
uv run python -m harness report $RunDir
```

생성된 solution.py는 평가기가 현재 사용자 권한의 별도 Python 프로세스에서 실행합니다. 임시 폴더와 시간 제한은 파일·네트워크 접근을 막지 않습니다. 민감 파일 없는 실습 장비에서 실행하세요.

## 5. 본인 결과만 commit/push
키·토큰·개인정보가 원문·로그·노트에 없는지 확인한 후 수행합니다. NOTES.md 작성과 REPORT.md 검토를 끝내고, **git add . 대신 본인 실행 폴더만** 추가합니다.

**저장소 루트**로 이동하고 $RunDir를 실제 본인 실행 경로로 설정한 뒤 실행합니다. 다른 stage가 있으면 자동으로 해제하지 않고 중단합니다.

```powershell
$Branch = git branch --show-current
if ($LASTEXITCODE -ne 0 -or $Branch -ne "main") { throw "저장소 main 브랜치에서 실행하세요." }
if ($RunDir -cnotmatch '^results/[a-z0-9][a-z0-9_-]{0,63}/[a-z0-9][a-z0-9_-]{0,63}$') {
    throw "본인 결과의 상대 경로를 정확히 설정하세요."
}
if (!(Test-Path -LiteralPath "$RunDir/REPORT.md") -or !(Test-Path -LiteralPath "$RunDir/NOTES.md")) {
    throw "보고서 또는 노트가 없습니다."
}
$Before = @(git diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $Before.Count -ne 0) { throw "기존 stage가 있습니다. 먼저 직접 확인·정리하세요." }
git add -- "$RunDir"
if ($LASTEXITCODE -ne 0) { throw "결과 추가 실패" }
$Staged = @(git diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $Staged.Count -eq 0) { throw "추가된 결과가 없습니다." }
$Other = @($Staged | Where-Object { !$_.StartsWith("$RunDir/", [System.StringComparison]::Ordinal) })
if ($Other.Count -ne 0) { throw "다른 파일이 stage에 포함되어 있습니다. 중단합니다." }
git diff --cached --stat
if ($LASTEXITCODE -ne 0) { throw "stage 확인 실패" }
# REPORT.md, NOTES.md, 원문·로그를 검토한 뒤 아래 명령을 수행합니다.
git commit -m "results: $Me $Model"
if ($LASTEXITCODE -ne 0) { throw "commit 실패: push하지 않습니다." }
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) { throw "rebase 실패: 충돌을 해결하기 전 push하지 않습니다." }
git push origin main
if ($LASTEXITCODE -ne 0) { throw "push 실패: 메시지를 확인하고 force push하지 마세요." }
```

다른 팀원이 먼저 push했으면 최신 main을 받아 rebase한 뒤 다시 push합니다. 충돌 시 자동 덮어쓰기나 force push를 하지 않습니다. 권한/보호 규칙이 main push를 막으면 저장소의 기존 PR 절차를 따릅니다.

results 폴더는 Git 추적 대상입니다. runs 폴더는 사전 검증·기존 2모델 실행의 임시 로그이며 계속 gitignore 대상입니다. 테스트 코드·모델 가중치·가상환경을 개인 성능 결과와 함께 바꾸지 않습니다.

## 팀 완료 체크
- 개인: 20회 실행 상태 확인 + REPORT.md + 작성된 NOTES.md + 근거 파일 + push.
- 팀: 서로 다른 로컬 2모델, 동일 PC 기준 비교, Cloud 5회, 참여 기록, 최종 모델 선정·한계 정리.
- 현재 패키지는 단위/모의 검증까지이며 실제 Windows/Ollama 장비 테스트는 팀에서 수행해야 합니다.
