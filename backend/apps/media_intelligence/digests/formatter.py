from collections import Counter


def format_daily_digest(items):
    if not items.exists():
        return "📊 **Daily Anioma Digest**\n\nNo significant Anioma-related news in the last 24 hours."

    total = items.count()
    high_severity = items.filter(severity="high").count()

    tags = []
    for item in items:
        tags.extend(item.semantic_tags)

    top_tags = Counter(tags).most_common(5)

    message = [
        "📊 **Daily Anioma Digest**",
        "",
        f"📰 Total relevant items: {total}",
        f"🔥 High-severity alerts: {high_severity}",
        "",
        "🔑 Top themes:"
    ]

    for tag, count in top_tags:
        message.append(f"• {tag} ({count})")

    message.append("")
    message.append("📌 Notable items:")

    for item in items[:3]:
        prefix = "🔥" if item.severity == "high" else "•"
        message.append(f"{prefix} {item.title}")

    return "\n".join(message)


def format_weekly_digest(items):
    if not items.exists():
        return "📊 **Weekly Anioma Digest**\n\nNo significant Anioma-related trends this week."

    severity_counts = Counter(items.values_list("severity", flat=True))

    tags = []
    for item in items:
        tags.extend(item.semantic_tags)

    top_tags = Counter(tags).most_common(7)

    message = [
        "📊 **Weekly Anioma Digest**",
        "",
        "📈 Severity breakdown:"
    ]

    for level, count in severity_counts.items():
        emoji = "🔥" if level == "high" else "•"
        message.append(f"{emoji} {level.title()}: {count}")

    message.append("")
    message.append("🔁 Recurring themes:")

    for tag, count in top_tags:
        message.append(f"• {tag} ({count})")

    return "\n".join(message)
