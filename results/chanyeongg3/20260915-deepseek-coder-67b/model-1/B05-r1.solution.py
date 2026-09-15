class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        key = key.strip().lower()
        if key in self._entries:
            if self._entries[key][0] != payload:
                raise ValueError("idempotency key reused with different payload")
            return self._entries[key][1]
        result = {"total": sum(payload.values())}
        self._entries[key] = (payload.copy(), result.copy())
        return result
