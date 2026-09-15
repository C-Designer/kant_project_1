# B09: 주문 단위 권한 검사
로그인만 확인하고 누구나 주문을 취소할 수 있는 문제를 수정하세요.

## 계약
- cancel_order(orders: dict[str, dict], order_id: str, actor_id: str, is_admin: bool = False) -> dict.
- orders의 각 값은 owner_id(str), status('pending' 또는 'cancelled')만 가진 사전. ID는 빈 문자열도 가능한 임의 문자열이고 대소문자를 구분합니다. 타입은 모두 유효하며 서로 다른 주문 값은 별개 사전입니다.
- 존재하지 않는 order_id는 관리자 여부와 관계없이 KeyError이며 전체 상태 불변.
- 기존 주문의 owner_id와 actor_id가 같거나 is_admin=True면 허용. 관리자 여부는 신뢰할 수 있는 서버가 전달합니다.
- 그 외에는 PermissionError이며 모든 주문 상태가 그대로여야 합니다. 이미 cancelled인 주문도 권한 검사 후에만 성공할 수 있습니다.
- 허용 시 대상 주문 status를 cancelled로 제자리 수정. owner_id 및 다른 주문은 그대로. 이미 cancelled면 멱등 성공.
- 성공 반환은 대상 주문의 독립적인 얕은 사본이며 반환 사전 수정은 저장된 주문에 영향 없음. 예외 메시지는 자유입니다.

## 제출
설명 없이 python fenced code block 정확히 하나로 전체 solution.py를 제출하세요. Python 3.12 표준 라이브러리만 사용합니다. 테스트는 pytest를 사용합니다. 네트워크·난수·시계는 금지합니다. 비공개 테스트는 모델에게만 숨기며 저장소 독자는 읽을 수 있습니다. 모든 테스트는 명시된 계약만 검증합니다.
