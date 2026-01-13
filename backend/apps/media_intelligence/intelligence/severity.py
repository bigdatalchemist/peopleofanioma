def classify_severity(item_data: dict) -> str:
    text = f"{item_data.get('title', '')} {item_data.get('content', '')}".lower()
    tags = set(item_data.get("semantic_tags", []))

    HIGH_TRIGGERS = [
        "violence", "killing", "attack", "riot",
        "clash", "protest", "arrest", "conflict",
        "election violence", "military", "terror"
    ]

    MEDIUM_TRIGGERS = [
        "election", "policy", "government",
        "court", "economy", "land dispute",
        "migration", "boundary"
    ]

    if any(word in text for word in HIGH_TRIGGERS):
        return "high"

    if any(word in text for word in MEDIUM_TRIGGERS):
        return "medium"

    if tags.intersection({"politics", "security", "economy"}):
        return "medium"

    return "low"
