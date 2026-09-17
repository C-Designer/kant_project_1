def update_profile(profile, patch):
    allowed = {"display_name", "bio", "alerts"}

    for key, value in patch.items():
        if key not in allowed or (key != "bio" and value is None):
            raise ValueError("invalid patch")

    profile.update(patch)
    return dict(profile)
