# B05 순차 요청의 멱등 키
같은 키 재시도의 잘못된 재사용과 가변 객체 공유 오류를 수정하세요.

## 계약
`class IdempotencyStore:`
- `def __init__(self):` 인수 없이 비어 있는 독립 저장소를 만듭니다.
- `def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:`
처음 보는 키이면 payload 값의 합을 계산해 `{"total": 합계}`를 반환하고, 그 키의 payload와 결과를 저장합니다. 기존 키와 **동일한 payload**로 재시도하면 저장된 결과를 반환합니다. 동일 여부는 dict 값의 동등성입니다(항목 순서 무관). 합계가 같더라도 항목 이름이나 값이 다르면 다른 payload입니다. 기존 키에 다른 payload를 보내면 정확히 `ValueError("idempotency key reused with different payload")`를 발생시키고 저장 상태를 그대로 유지합니다.
키 문자열은 공백 제거/대소문자 변환 없이 정확히 구별합니다. 서로 다른 키와 서로 다른 저장소 인스턴스는 독립적입니다.

## 유효 입력 및 변경
호출은 단일 프로세스에서 순차적으로만 일어납니다. 동시성, 영속성, 만료, 네트워크 처리는 필요 없습니다. key는 빈 문자열이 아닌 str이고, payload는 str 키와 bool이 아닌 int 값만 포함한 dict입니다. 빈 dict와 음수 값도 허용합니다. 입력 오류 처리는 요구하지 않습니다. payload를 변경하지 마세요. 저장된 payload는 호출 당시의 스냅샷이어야 하며, 호출자가 나중에 입력을 수정해도 저장 상태는 변하지 않습니다. 반환 dict도 매번 독립적이어야 하며 수정해도 저장 결과나 다른 반환값이 변하면 안 됩니다.

## 제출 형식
Python 3.12 표준 라이브러리만 사용하세요. 정확히 하나의 `python` fenced code block에 전체 `solution.py` 내용을 제출하세요. 설명, 테스트, 의존성 파일은 제출하지 마세요. 공개 테스트와 숨김 테스트 모두 아래 명시된 계약만 검사합니다.
