def update_profile(profile: dict, patch: dict) -> dict:
    allowed = {"display_name", "bio", "alerts"}

    for key, value in patch.items():
        if key not in allowed:
            raise ValueError("invalid patch")
        if key in {"display_name", "alerts"} and value is None:
            raise ValueError("invalid patch")

    profile.update(patch)
    return dict(profile)
