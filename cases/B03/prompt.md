# B03 선택적 조회 옵션 검증
기본값 적용과 bool/int 혼동으로 잘못 허용되는 옵션을 수정하세요.

## 계약
`def validate_options(limit=None, offset=None, include_archived=None) -> dict`
None 또는 생략에만 기본값을 적용합니다: limit=20, offset=0, include_archived=False. 반환 dict의 키는 정확히 `limit`, `offset`, `include_archived`입니다. limit는 bool이 아닌 int이고 1~100, offset는 bool이 아닌 int이고 0 이상, include_archived는 bool이어야 합니다. 형 변환은 하지 마세요.
잘못된 값은 아래 **정확한 메시지**의 ValueError를 발생시킵니다. 여러 값이 잘못되면 limit, offset, include_archived 순서의 첫 오류만 반환합니다.
- limit: `limit must be an integer between 1 and 100`
- offset: `offset must be a non-negative integer`
- include_archived: `include_archived must be a boolean`

## 입력 범위 및 변경
각 인수는 None, bool, int, float, str, list, dict 중 하나입니다. 사용자 정의 클래스는 없습니다. 입력 객체를 변경하지 마세요. 호출마다 새로운 결과 dict를 반환하세요.

## 제출 형식
Python 3.12 표준 라이브러리만 사용하세요. 정확히 하나의 `python` fenced code block에 전체 `solution.py` 내용을 제출하세요. 설명, 테스트, 의존성 파일은 제출하지 마세요. 공개 테스트와 숨김 테스트 모두 아래 명시된 계약만 검사합니다.
