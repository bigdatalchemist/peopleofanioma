def is_notification_eligible(news_item) -> bool:
    """
    Phase 2.5 — Policy gate.
    Decides if this content is worthy of notification at all.
    """

    # 1️⃣ Confidence gate
    if news_item.confidence_score < 0.6:
        return False

    # 2️⃣ Severity gate
    if news_item.severity == "low":
        return False

    # 3️⃣ Must actually be Anioma-related
    if not news_item.is_anioma_related:
        return False

    return True
