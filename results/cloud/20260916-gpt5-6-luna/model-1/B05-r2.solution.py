class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            stored_payload, stored_result = self._entries[key]
            if stored_payload != payload:
                raise ValueError("idempotency key reused with different payload")
            return dict(stored_result)

        stored_payload = dict(payload)
        stored_result = {"total": sum(payload.values())}
        self._entries[key] = (stored_payload, stored_result)
        return dict(stored_result)
