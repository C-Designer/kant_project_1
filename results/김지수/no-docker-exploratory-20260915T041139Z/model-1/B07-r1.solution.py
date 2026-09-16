def update_profile(profile, patch):
    for key, value in patch.items():
        if key not in {"display_name", "bio", "alerts"} or (value is None and key != "bio"):
            raise ValueError("invalid patch")
    updated_profile = profile.copy()
    for key, value in patch.items():
        if key == "bio" and value is None:
            updated_profile.pop(key, None)
        else:
            updated_profile[key] = value
    return updated_profile
