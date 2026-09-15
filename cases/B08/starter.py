class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class FakeNotificationService:
    def __init__(self, failures=()):
        self._failures = list(failures)
        self.calls = 0
        self.effects = []
        self._receipts = {}

    def send(self, key, message):
        self.calls += 1
        event = self._failures.pop(0) if self._failures else "ok"
        if event == "before":
            raise TransientError("before delivery")
        if event == "permanent":
            raise PermanentError("rejected")
        if key not in self._receipts:
            self.effects.append((key, message))
            self._receipts[key] = "receipt:" + key
        if event == "after":
            raise TransientError("response lost")
        return self._receipts[key]


def send_notification(service, key, message, max_attempts=3):
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    for attempt in range(max_attempts):
        try:
            return service.send(key if attempt == 0 else key + ":retry:" + str(attempt), message)
        except (TransientError, PermanentError):
            if attempt == max_attempts - 1:
                raise
