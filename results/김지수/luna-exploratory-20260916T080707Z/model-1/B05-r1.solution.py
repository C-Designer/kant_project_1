class IdempotencyStore:
    def __init__(self):
        self._entries: dict[str, tuple[dict[str, int], dict[str, int]]] = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            stored_payload, stored_result = self._entries[key]
            if stored_payload != payload:
                raise ValueError("idempotency key reused with different payload")
            return stored_result.copy()

        stored_payload = payload.copy()
        result = {"total": sum(stored_payload.values())}
        stored_result = result.copy()
        self._entries[key] = (stored_payload, stored_result)
        return result.copy()
