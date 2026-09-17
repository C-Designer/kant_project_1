class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            stored_payload, stored_result = self._entries[key]
            if stored_payload != payload:
                raise ValueError("idempotency key reused with different payload")
            return stored_result.copy()

        payload_snapshot = payload.copy()
        result = {"total": sum(payload_snapshot.values())}
        self._entries[key] = (payload_snapshot, result.copy())
        return result
