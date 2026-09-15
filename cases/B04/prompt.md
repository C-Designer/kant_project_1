# B04 시간대가 있는 날짜 구간 필터
서로 다른 UTC 오프셋의 타임스탬프를 같은 절대 시각 기준으로 비교하세요.

## 계약
`def select_window(timestamps: list[datetime], start: datetime, end: datetime) -> list[datetime]`
구간은 시작 포함, 끝 제외인 `[start, end)`입니다. datetime의 날짜/시계 표시가 아니라 절대 시각으로 비교하세요. 입력 순서와 중복을 보존한 새 목록을 반환하며 원래 datetime 값(시간대 포함)을 유지합니다. start와 end가 같은 절대 시각이면 빈 목록입니다.
검증 순서는 다음과 같습니다. 먼저 start, end, timestamps의 모든 원소 순서로 확인하여 naive datetime이 하나라도 있으면 `ValueError("all timestamps must be timezone-aware")`를 발생시킵니다. 그 다음 start가 end보다 늦으면 `ValueError("start must not be after end")`를 발생시킵니다. 빈 목록이나 구간 밖 원소에도 이 검증은 적용됩니다.

## 입력 범위 및 변경
모든 값은 표준 datetime.datetime 객체입니다. 시간대는 None(naive) 또는 datetime.timezone의 UTC/고정 오프셋입니다. 다른 tzinfo 클래스나 문자열은 입력되지 않습니다. 날짜는 2000~2100년입니다. 입력 목록과 datetime을 변경하지 마세요. 외부 패키지, 현재 시각, 시스템 로컬 시간대에 의존하지 마세요.

## 제출 형식
Python 3.12 표준 라이브러리만 사용하세요. 정확히 하나의 `python` fenced code block에 전체 `solution.py` 내용을 제출하세요. 설명, 테스트, 의존성 파일은 제출하지 마세요. 공개 테스트와 숨김 테스트 모두 아래 명시된 계약만 검사합니다.
