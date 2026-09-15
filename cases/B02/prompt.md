# B02 1부터 시작하는 페이지 조회
페이지 경계와 메타데이터 오류를 수정하세요.

## 계약
`def paginate(items: list[int], page: int, page_size: int) -> dict`
`page`는 1부터 시작합니다. 원래 순서대로 해당 페이지를 잘라 다음 키만 가진 dict를 반환하세요: `items`(새 목록), `page`(요청한 번호), `page_size`, `total`(전체 항목 수), `total_pages`(올림한 페이지 수), `has_next`(page < total_pages인 bool). 빈 목록의 total_pages는 0입니다. 범위를 넘은 페이지의 items는 빈 목록이며 요청 page를 그대로 유지합니다.

## 유효 입력 및 변경
items는 int 목록, page와 page_size는 bool이 아닌 양의 int입니다. 입력 오류 처리는 요구하지 않습니다. 입력 목록을 변경하지 마세요. 반환된 items 목록과 원본 목록은 서로 독립적이어야 합니다.

## 제출 형식
Python 3.12 표준 라이브러리만 사용하세요. 정확히 하나의 `python` fenced code block에 전체 `solution.py` 내용을 제출하세요. 설명, 테스트, 의존성 파일은 제출하지 마세요. 공개 테스트와 숨김 테스트 모두 아래 명시된 계약만 검사합니다.
