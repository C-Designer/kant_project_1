class IdempotencyStore:
    def __init__(self):
        self._entries = {}

    def execute(self, key: str, payload: dict[str, int]) -> dict[str, int]:
        if key in self._entries:
            return self._entries[key][1]
        result = {"total": sum(payload.values())}
        self._entries[key] = (payload, result)
        return result
