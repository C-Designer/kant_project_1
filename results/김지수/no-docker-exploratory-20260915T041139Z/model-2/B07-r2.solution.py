def update_profile(profile, patch):
    for key, value in patch.items():
        if key not in {"display_name", "bio", "alerts"}:
            raise ValueError("invalid patch")
        if value is None and key != "bio":
            raise ValueError("invalid patch")
    profile.update({k: v for k, v in patch.items() if v is not None})
    return dict(profile)
