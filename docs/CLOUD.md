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

| 문제 | 호출 상태 | 정확한 모델 ID | 응답 시간(초) | 입력 토큰 | 출력 토큰 (추론 토큰) | 추정 비용 | 원본 파일 |
|---|---|---|---|---|---|---|---|
| B01 | 성공 / solved | gpt-5.6-luna | 7.69 | 555 | 430 (318) | $0.00063 | `results/cloud/20260916-gpt5-6-luna/model-1/B01-r1.raw.json` |
| B04 | 성공 / solved | gpt-5.6-luna | 4.36 | 882 | 233 (123) | $0.00046 | `.../B04-r1.raw.json` |
| B06 | 성공 / solved | gpt-5.6-luna | 2.95 | 603 | 199 (86) | $0.00036 | `.../B06-r1.raw.json` |
| B08 | 성공 / solved | gpt-5.6-luna | 9.17 | 1,234 | 806 (490) | $0.00121 | `.../B08-r1.raw.json` |
| B10 | 성공 / solved | gpt-5.6-luna | 12.14 | 1,217 | 731 (512) | $0.00112 | `.../B10-r1.raw.json` |
| **합계** | 5/5 | | 평균 7.26 (n=5) | 4,491 | 2,399 (1,529) | **약 $0.0038** | |

**위 표의 출처:** errorn이 2026-09-16에 `scripts/cloud_run_model.py`로 실행한 10문제 × 2회(20회) 중 사전 지정 5문제의 **1회차를 사후 추출**한 값입니다. 응답 시간은 `results.jsonl`의 `elapsed_seconds`(네트워크 포함), 토큰은 제공자 JSON 원본의 `usage`에서 읽었습니다. 실행 시 `temperature` 지정이 거부돼(HTTP 400) 서버 기본값으로 호출됐고, `max_output_tokens=2048`, 대화 이력 없음, 재시도 없음 조건입니다. 전체 20회는 20/20 해결, 입력 15,890 / 출력 6,567(추론 3,580) 토큰이며 참고용입니다. 김지수의 별도 20회 실행(`results/김지수/luna-exploratory-20260916T080707Z/`, Responses API)도 20/20으로 같은 결과였습니다.

**비용 계산:** 단가는 OpenAI 공식 가격표(https://developers.openai.com/api/docs/pricing, 2026-09-17 확인, USD, short context) 기준 입력 $0.20 / 출력 $1.20 per 1M 토큰이며, 추론 토큰은 출력 토큰에 포함되어 과금됩니다. 5회 추정 비용 = 4,491 × $0.20/1M + 2,399 × $1.20/1M ≈ $0.0009 + $0.0029 = **약 $0.0038**. 전체 20회는 15,890 × $0.20/1M + 6,567 × $1.20/1M ≈ **약 $0.0111**. 이 값은 토큰 수 × 공개 단가의 추정치이며, 실제 청구 내역은 OpenAI 사용량 페이지에서 별도 확인합니다.

추정 비용에는 입력·출력 단가, 통화, 단가 기준일과 출처를 함께 적습니다. 실제 청구 내역과는 구분합니다. API 키·요청 Authorization 헤더·인증 정보는 저장소와 로그에 포함하지 않습니다.

## 3. 동일 Python 테스트로 평가
```powershell
uv run python -m harness import-cloud --bundle runs/cloud-prompts --responses runs/cloud-responses --model "PROVIDER/EXACT-MODEL-ID" --out runs/cloud-001
uv run python -m harness summarize runs/cloud-001
```

`runs/cloud-responses`에 응답 파일 5개를 둡니다. 없는 파일은 missing_response로 기록됩니다. 호출 실패인지 실험 누락인지 API 호출 기록에서 구분하세요. 품질 결과에 없는 토큰·시간·비용은 null이며 위 원본 측정 표로 보완합니다.

## 4. 비교 범위
Cloud 5회 대 Local A/B 각 **같은 5문제의 10회**를 비교합니다. 전체 로컬 20회의 성적을 Cloud 5회와 바로 비교하지 않습니다. 로컬의 좋은 반복만 골라 사용하지 않습니다. 사례별 두 반복과 Cloud 1회의 결과를 모두 표시합니다. 상대적인 로컬 모델 선정과 Cloud 운영 권고는 별개 결론입니다.
