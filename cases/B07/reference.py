def update_profile(profile, patch):
    for key, value in patch.items():
        if key not in {"display_name", "bio", "alerts"} or (value is None and key != "bio"):
            raise ValueError("invalid patch")
    profile.update(patch)
    return dict(profile)
