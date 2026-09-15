class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            saved_payload, saved_result = self._entries[key]
            if saved_payload != payload:
                raise ValueError("idempotency key reused with different payload")
            return saved_result.copy()
        result = {"total": sum(payload.values())}
        self._entries[key] = (payload.copy(), result.copy())
        return result
