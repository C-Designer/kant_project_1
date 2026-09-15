def update_profile(profile, patch):
    valid_keys = {"display_name", "bio", "alerts"}
    for key, value in patch.items():
        if key not in valid_keys or (value is None and key != "bio"):
            raise ValueError("invalid patch")
    
    updated_profile = profile.copy()
    for key, value in patch.items():
        if key == "bio" and value is None:
            del updated_profile[key]
        else:
            updated_profile[key] = value
    
    return updated_profile
