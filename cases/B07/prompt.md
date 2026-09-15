# B07: 부분 수정의 누락·null·falsy 구분
truthiness 기반 부분 수정으로 소개 삭제와 알림 끄기가 무시되는 문제를 수정하세요.

## 계약
- update_profile(profile: dict, patch: dict) -> dict.
- profile은 display_name(str), bio(str 또는 None), alerts(bool) 세 키를 모두 가지며 다른 키는 없습니다.
- patch는 별개 사전. 누락한 키는 그대로 보존. 빈 patch는 변경 없음.
- bio의 명시적 None은 삭제이며 그대로 저장. display_name과 bio의 빈 문자열 및 alerts=False도 그대로 저장.
- 알 수 없는 patch 키 또는 display_name/alerts의 None은 ValueError. 어떤 키 순서에서도 실패 시 profile 전체가 변경되지 않아야 합니다.
- 이외 잘못된 타입은 입력되지 않습니다.
- 성공하면 전달받은 profile 사전을 제자리 수정하고 독립적인 얕은 사본을 반환. 반환값 수정은 profile에 영향 없음. patch는 성공/실패 모두 수정하지 않습니다.

## 제출
설명 없이 python fenced code block 정확히 하나로 전체 solution.py를 제출하세요. Python 3.12 표준 라이브러리만 사용합니다. 테스트는 pytest를 사용합니다. 네트워크·난수·시계는 금지합니다. 비공개 테스트는 모델에게만 숨기며 저장소 독자는 읽을 수 있습니다. 모든 테스트는 명시된 계약만 검증합니다.
