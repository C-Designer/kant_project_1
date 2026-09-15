# Cloud API 비교: 고정 5문제 × 각 1회

발제문 STEP 7에 따라 **B01·B04·B06·B08·B10을 각 1회** 호출합니다. 총 5회이며, 같은 문제의 로컬 2회 결과를 모두 사용합니다. Cloud API 호출 비용은 별도이고 이 저장소 준비 중에는 호출하지 않았습니다.

## 1. 같은 입력 내보내기
```powershell
uv run python -m harness export-cloud --out runs/cloud-prompts
```

생성된 `B01.prompt.txt` 등의 전문을 수업에서 제공한 `02_luna_chat.py` 또는 승인된 API 호출 코드의 입력으로 사용합니다. **웹 채팅 제품이 아니라 과제에서 지정한 API**를 사용합니다. 각 호출은 대화 이력을 초기화하고 첫 응답만 기록합니다. reference.py와 test_hidden.py는 전달하지 않습니다.

모델 ID·출력 한도·샘플링 옵션을 사전 고정하고 Ollama와 동일 설정이 지원되지 않으면 차이를 기록합니다. 응답을 받은 뒤 문구나 코드 블록을 편집하지 마세요. 제공자 JSON 원본은 별도 보존하고, 응답 본문의 정확한 텍스트를 UTF-8 파일 `B01-r1.txt`처럼 저장합니다. 호출 실패는 빈 성공 응답으로 대체하지 말고 오류 기록을 남깁니다. 자동 재시도는 사용하지 않습니다.

## 2. 반드시 별도 기록할 API 측정치
현재 import 기능은 응답 텍스트의 품질만 채점하므로, API 성능·비용은 아래 표와 제공자 원본으로 연결해야 합니다. 수동으로 옮긴 측정치를 자동 측정처럼 표시하지 않습니다.

| 문제 | 호출 상태 | 정확한 모델 ID | 응답 시간(초) | 입력 토큰 | 출력 토큰 | 추정 비용 | 원본 파일 |
|---|---|---|---|---|---|---|---|
| B01 | | | | | | | |
| B04 | | | | | | | |
| B06 | | | | | | | |
| B08 | | | | | | | |
| B10 | | | | | | | |

추정 비용에는 입력·출력 단가, 통화, 단가 기준일과 출처를 함께 적습니다. 실제 청구 내역과는 구분합니다. API 키·요청 Authorization 헤더·인증 정보는 저장소와 로그에 포함하지 않습니다.

## 3. 동일 Docker 테스트로 평가
```powershell
uv run python -m harness import-cloud --bundle runs/cloud-prompts --responses runs/cloud-responses --model "PROVIDER/EXACT-MODEL-ID" --out runs/cloud-001
uv run python -m harness summarize runs/cloud-001
```

`runs/cloud-responses`에 응답 파일 5개를 둡니다. 없는 파일은 missing_response로 기록됩니다. 호출 실패인지 실험 누락인지 API 호출 기록에서 구분하세요. 품질 결과에 없는 토큰·시간·비용은 null이며 위 원본 측정 표로 보완합니다.

## 4. 비교 범위
Cloud 5회 대 Local A/B 각 **같은 5문제의 10회**를 비교합니다. 전체 로컬 20회의 성적을 Cloud 5회와 바로 비교하지 않습니다. 로컬의 좋은 반복만 골라 사용하지 않습니다. 사례별 두 반복과 Cloud 1회의 결과를 모두 표시합니다. 상대적인 로컬 모델 선정과 Cloud 운영 권고는 별개 결론입니다.
