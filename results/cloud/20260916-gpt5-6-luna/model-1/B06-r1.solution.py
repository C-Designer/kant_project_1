class ProfileService:
    def __init__(self, profiles):
        self._profiles = {user_id: dict(profile) for user_id, profile in profiles.items()}
        self._cache = {}

    def get_profile(self, user_id):
        if user_id not in self._profiles:
            raise KeyError(user_id)

        if user_id not in self._cache:
            self._cache[user_id] = dict(self._profiles[user_id])

        return dict(self._cache[user_id])
