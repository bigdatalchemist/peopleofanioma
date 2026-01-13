def compute_confidence_score(item_data: dict) -> float:
    score = 0.0

    categories = set(item_data.get("detection_methods", []))
    entities = item_data.get("entities", {})
    semantic_tags = item_data.get("semantic_tags", [])
    relevance = item_data.get("relevance_score", 0.0)
    source_type = item_data.get("source_type", "")

    # 1️⃣ Direct evidence
    if "direct_mention" in categories:
        score += 0.35

    # 2️⃣ Semantic match
    if "semantic_match" in categories or semantic_tags:
        score += 0.25

    # 3️⃣ Location grounding
    if "location_based" in categories:
        score += 0.20

    # 4️⃣ Source reliability
    trusted_sources = {
        "news_aggregator": 0.10,
        "website": 0.08,
        "twitter": 0.04,
        "facebook": 0.03,
    }
    score += trusted_sources.get(source_type, 0.02)

    # 5️⃣ Existing relevance score
    score += min(relevance, 1.0) * 0.10

    return round(min(score, 1.0), 3)
