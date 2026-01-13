from datetime import timedelta
from django.utils import timezone
from apps.media_intelligence.models import TrackedNewsItem


def get_daily_digest_items():
    since = timezone.now() - timedelta(days=1)

    return TrackedNewsItem.objects.filter(
        published_date__gte=since,
        confidence_score__gte=0.6,
        is_anioma_related=True
    ).order_by("-severity", "-relevance_score")


def get_weekly_digest_items():
    since = timezone.now() - timedelta(days=7)

    return TrackedNewsItem.objects.filter(
        published_date__gte=since,
        confidence_score__gte=0.6,
        is_anioma_related=True
    )
