# B08: 알림 재시도와 외부 부수 효과
응답 유실은 이미 알림을 보낸 뒤에도 발생할 수 있습니다. 재시도마다 다른 키를 쓰거나 영구 오류도 재시도하는 버그를 수정하세요. 단순 중복 요청 저장 문제와 달리, 이 문제의 핵심은 오류 분류·시도 한도·성공 후 응답 유실을 함께 처리하는 재시도 래퍼입니다.

## API와 계약
- TransientError(Exception), PermanentError(Exception)를 공개합니다.
- send_notification(service, key: str, message: str, max_attempts: int = 3) -> str.
- service는 send(key, message) -> str 인터페이스만 필요합니다. 아래 fake 외의 동일 인터페이스 객체도 허용합니다. 반환한 문자열을 그대로 반환하며 첫 성공 즉시 중단합니다.
- 일시적 TransientError만 재시도합니다. PermanentError 및 다른 예외는 즉시 그대로 전파합니다. 모두 실패하면 마지막 TransientError를 전파합니다. 예외 메시지·동일 예외 객체를 보존합니다.
- max_attempts는 최초 호출 포함 총 시도 수. 1 이상 정수이며 0/음수도 테스트합니다. 1 미만이면 service 호출 없이 ValueError. bool 및 비정수는 입력되지 않습니다.
- 매 시도에 원래 key와 message를 변경 없이 전달합니다. sleep, 별도 네트워크, 백오프는 없습니다.
- key/message는 빈 문자열도 유효. 동일 서비스에서 같은 key는 항상 같은 message로 사용합니다.

## 함께 제출할 결정론적 fake의 계약
- FakeNotificationService(failures=()) 및 send(key: str, message: str) -> str.
- failures는 ok/before/after/permanent 문자열의 유한 list 또는 tuple입니다. 생성자가 사본을 보관하며 원본은 수정하지 않습니다.
- calls는 생성 시 0이고 send 호출마다 1 증가하는 공개 정수. effects는 생성 시 빈 공개 list이며 실제 전달을 (key, message) 튜플로 전달 순서대로 기록합니다. 호출자는 이 속성을 읽기만 합니다.
- 매 send 호출은 failures의 다음 항목 하나를 소비합니다. 소진 후에는 ok. 이미 전달된 key에도 항목을 소비합니다.
- before: 전달 없이 TransientError. permanent: 전달 없이 PermanentError.
- ok/after: 아직 전달하지 않은 key면 effects에 한 번 기록하고 영수증을 저장합니다. 이미 전달한 key는 새 효과 없이 기존 영수증을 사용합니다. 영수증 문자열은 'receipt:' + key.
- ok는 영수증 반환. after는 전달/중복제거 처리 후 TransientError. 오류 메시지는 fake에 한해 자유입니다.
- 서로 다른 key와 서비스 인스턴스는 독립적입니다. 그 외 잘못된 입력은 없습니다.

## 제출
설명 없이 python fenced code block 정확히 하나로 전체 solution.py를 제출하세요. Python 3.12 표준 라이브러리만 사용합니다. 테스트는 pytest를 사용합니다. 네트워크·난수·시계는 금지합니다. 비공개 테스트는 모델에게만 숨기며 저장소 독자는 읽을 수 있습니다. 모든 테스트는 명시된 계약만 검증합니다.
