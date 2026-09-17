class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        stored_payload, stored_result = self._entries.get(key, (None, None))
        if stored_payload is None:  # First request
            result = {"total": sum(payload.values())}
            self._entries[key] = (payload.copy(), result.copy())
            return result
        elif payload == stored_payload:  # Identical retry
            return stored_result
        else:  # Changed payload
            raise ValueError("idempotency key reused with different payload")
