# B10: 재고 차감과 주문 생성의 롤백
재고를 차감한 뒤 주문 생성 또는 후처리가 실패하면 일부 상태만 남습니다. 단일 스레드의 메모리 사전 두 개에서 전체 성공 또는 전체 취소를 구현하세요. DB, 동시성, 외부 서비스, 재시도는 범위 밖입니다.

## API 및 정상 입력
- place_order(inventory: dict[str, int], orders: dict[str, dict], order_id: str, items: dict[str, int], fail_at: str | None = None) -> dict.
- inventory는 SKU → 0 이상 정수 재고. items는 SKU → 양의 정수 수량인 비어 있지 않은 사전. 같은 SKU는 한 번만 나타납니다. bool 수량, 잘못된 타입/수량, 빈 items는 입력되지 않습니다.
- SKU와 주문 ID는 빈 문자열도 가능한 임의 문자열이며 대소문자를 구분합니다.
- 기존 orders 값은 {'items': {SKU: 양의 정수}, 'status': 'confirmed'} 형식입니다. 기존 주문의 SKU가 현재 inventory에 있을 필요는 없습니다.
- 전달된 사전들은 서로 별개이며 중첩 사전 별칭도 없습니다. fail_at은 None, 'after_stock', 'after_order'만 입력됩니다.

## 계약
1. order_id가 이미 있거나, items에 없는 재고 SKU가 있거나, 하나라도 재고가 부족하면 ValueError. 모든 상태와 items는 그대로. 검증 오류가 있으면 fail_at보다 우선합니다. 여러 검증 오류 중 메시지/순서는 자유입니다.
2. 성공 시 전달받은 inventory를 제자리 수정해 각 수량을 차감합니다. 정확히 남은 수량만큼 주문 가능하며 재고 0인 SKU도 삭제하지 않습니다. 관련 없는 재고는 그대로.
3. 전달받은 orders에 order_id 키로 {'items': items의 사본, 'status': 'confirmed'}를 추가합니다. 기존 주문은 그대로. 반환값은 새 주문의 깊은 사본이며 반환값/입력 items의 이후 수정은 저장 주문에 영향 없음.
4. fail_at='after_stock'이면 모든 재고 차감 직후, 주문 추가 전에 RuntimeError를 발생시킵니다. 'after_order'이면 주문 추가 직후 RuntimeError. 두 경우 모두 inventory와 orders를 호출 직전 내용으로 완전히 복원하고 RuntimeError를 호출자에게 전파합니다. 예외 메시지는 자유입니다.
5. 실패는 주문 ID를 예약하지 않으며 수정된 재고나 유령 주문을 남기지 않습니다. 실패 후 같은 인자로 fail_at=None 호출 시 정상 성공할 수 있습니다. 내부 중간 단계/중첩 사전 객체 동일성은 검사하지 않고 최종 관찰 상태만 검사합니다.
6. 입력 items는 성공/실패 모두 수정하지 않습니다. 구현에 전역 상태를 사용해 호출 간 상태가 섞이면 안 됩니다.

## 제출
설명 없이 python fenced code block 정확히 하나로 전체 solution.py를 제출하세요. Python 3.12 표준 라이브러리만 사용합니다. 테스트는 pytest를 사용합니다. 네트워크·난수·시계는 금지합니다. 비공개 테스트는 모델에게만 숨기며 저장소 독자는 읽을 수 있습니다. 모든 테스트는 명시된 계약만 검증합니다.
