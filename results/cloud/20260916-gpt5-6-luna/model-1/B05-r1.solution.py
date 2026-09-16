class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            stored_payload, total = self._entries[key]
            if stored_payload != payload:
                raise ValueError("idempotency key reused with different payload")
            return {"total": total}

        payload_snapshot = payload.copy()
        total = sum(payload_snapshot.values())
        self._entries[key] = (payload_snapshot, total)
        return {"total": total}
