from apps.media_intelligence.notifications.manager import NotificationManager
from apps.media_intelligence.digests.query import (
    get_daily_digest_items,
    get_weekly_digest_items,
)
from apps.media_intelligence.digests.formatter import (
    format_daily_digest,
    format_weekly_digest,
)


def send_daily_digest():
    items = get_daily_digest_items()
    message = format_daily_digest(items)

    manager = NotificationManager()
    manager.send_notification(
        {
            "title": "Daily Anioma Digest",
            "content": message,
            "source": "Anioma Intelligence",
            "url": "",
        },
        notification_type="all",
    )


def send_weekly_digest():
    items = get_weekly_digest_items()
    message = format_weekly_digest(items)

    manager = NotificationManager()
    manager.send_notification(
        {
            "title": "Weekly Anioma Digest",
            "content": message,
            "source": "Anioma Intelligence",
            "url": "",
        },
        notification_type="all",
    )
