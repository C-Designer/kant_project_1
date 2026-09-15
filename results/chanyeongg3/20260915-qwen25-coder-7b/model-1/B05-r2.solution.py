class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            stored_payload, result = self._entries[key]
            if stored_payload == payload:
                return result
            else:
                raise ValueError("idempotency key reused with different payload")
        result = {"total": sum(payload.values())}
        self._entries[key] = (payload, result)
        return result
