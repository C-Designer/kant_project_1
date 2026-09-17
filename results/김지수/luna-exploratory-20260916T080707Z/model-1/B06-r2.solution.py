class ProfileService:
    def __init__(self, profiles: dict[str, dict[str, str]]):
        self._profiles = {user_id: dict(profile) for user_id, profile in profiles.items()}
        self._cache: dict[str, dict[str, str]] = {}

    def get_profile(self, user_id: str) -> dict[str, str]:
        if user_id not in self._profiles:
            raise KeyError(user_id)

        if user_id not in self._cache:
            self._cache[user_id] = dict(self._profiles[user_id])

        return dict(self._cache[user_id])
