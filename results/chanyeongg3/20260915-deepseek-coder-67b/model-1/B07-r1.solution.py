def update_profile(profile, patch):
    for key, value in patch.items():
        if key not in {"display_name", "bio", "alerts"} or (value is None and key != "bio"):
            raise ValueError("invalid patch")
        if value is None and key in {"display_name", "bio"}:
            profile[key] = ""
        elif key == "alerts" and value is False:
            profile[key] = False
        elif value is not None:
            profile[key] = value
    return dict(profile)
