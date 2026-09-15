def update_profile(profile, patch):
    for key, value in patch.items():
        if key not in {"display_name", "bio", "alerts"} or (value is None and key != "bio"):
            raise ValueError("invalid patch")
    profile.update({k: v for k, v in patch.items() if v})
    return dict(profile)
