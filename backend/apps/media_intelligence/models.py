# peopleofanioma/backend/apps/media_intelligence/models.py
from django.db import models
from django.utils import timezone
import uuid

class NewsSource(models.Model):
    SOURCE_TYPES = [
        ('website', 'Website/Blog'),
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('reddit', 'Reddit'),
        ('youtube', 'YouTube'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('news_aggregator', 'News Aggregator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    platform_specific_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    check_interval = models.IntegerField(default=15)  # minutes
    last_checked = models.DateTimeField(null=True, blank=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['url', 'source_type']
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"

class TrackedNewsItem(models.Model):
    CONTENT_CATEGORIES = [
        ('direct_mention', 'Direct Anioma Mention'),
        ('semantic_match', 'Semantic Match'),
        ('location_based', 'Location-Based'),
        ('cultural_match', 'Cultural/Thematic Match'),
        ('person_mention', 'Person/Figure Mention'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='news_items')
    title = models.TextField()
    content = models.TextField()
    url = models.URLField(max_length=1000, unique=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateTimeField()
    scraped_date = models.DateTimeField(auto_now_add=True)
    platform_specific_data = models.JSONField(default=dict)
    
    # NLP Analysis Fields
    categories = models.JSONField(default=list)
    keywords = models.JSONField(default=list)
    entities = models.JSONField(default=dict)
    sentiment_score = models.FloatField(null=True, blank=True)
    relevance_score = models.FloatField(default=0.0)
    is_anioma_related = models.BooleanField(default=False)
    semantic_tags = models.JSONField(default=list)
    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    confidence_score = models.FloatField(default=0.0)
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='low',
        db_index=True
    )
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)



    # Metadata
    has_been_notified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    requires_followup = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['published_date']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['is_anioma_related']),
        ]
        ordering = ['-published_date']
    
    def __str__(self):
        return f"{self.title[:100]}..."
    
    def save(self, *args, **kwargs):
        """
        Final safety net:
        Ensure content_hash is always generated,
        even if an object is saved outside the crawler.
        """
        if not self.content_hash:
            from apps.media_intelligence.utils.hash_utils import generate_content_hash
            self.content_hash = generate_content_hash(
                self.title or "",
                self.content or ""
            )

        super().save(*args, **kwargs)


class SemanticPattern(models.Model):
    """Store semantic patterns for Anioma-related content detection"""
    name = models.CharField(max_length=255)
    pattern_type = models.CharField(max_length=50, choices=[
        ('keyword', 'Keyword'),
        ('phrase', 'Phrase'),
        ('entity', 'Named Entity'),
        ('topic', 'Topic Cluster'),
        ('location', 'Location'),
        ('cultural', 'Cultural Concept'),
    ])
    pattern = models.TextField()  # Could be regex, keyword list, or ML pattern
    weight = models.FloatField(default=1.0)  # Importance weight
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    
    def __str__(self):
        return f"{self.name} ({self.pattern_type})"

class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    news_item = models.ForeignKey(TrackedNewsItem, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    sent_to = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    response = models.JSONField(default=dict, blank=True)
