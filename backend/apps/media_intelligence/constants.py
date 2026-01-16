# backend/apps/media_intelligence/constants.py
from django.db import models

class SourceType(models.TextChoices):
    WEBSITE = "website", "Website"
    TWITTER = "twitter", "Twitter"
    FACEBOOK = "facebook", "Facebook"
    TIKTOK = "tiktok", "TikTok"
    RSS = "rss", "RSS Feed"
