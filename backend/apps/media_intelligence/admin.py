# apps/media_intelligence/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from apps.media_intelligence.notifications.manager import NotificationManager


from .models import (
    TrackedNewsItem,
    NewsSource,
    SemanticPattern,
    NotificationLog
)

# ==========================
# NewsSource Admin
# ==========================
@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "source_type",
        "is_active",
        "check_interval",
        "last_checked",
    )
    list_filter = ("source_type", "is_active")
    search_fields = ("name", "url")
    readonly_fields = ("last_checked",)


# ==========================
# TrackedNewsItem (Editorial Core)
# ==========================
@admin.register(TrackedNewsItem)
class TrackedNewsItemAdmin(admin.ModelAdmin):
    list_select_related = ("source",)

    list_display = (
        "short_title",
        "severity_badge",
        "confidence_badge",
        "relevance_score",
        "source",
        "published_date",
        "is_verified",
        "has_been_notified",
    )

    list_filter = (
        "severity",
        "is_verified",
        "has_been_notified",
        "is_anioma_related",
        "source__source_type",
        "published_date",
    )

    search_fields = (
        "title",
        "content",
        "url",
    )

    ordering = ("-published_date",)

    readonly_fields = (
        "content_hash",
        "scraped_date",
        "confidence_score",
        "relevance_score",
        "sentiment_score",
    )

    fieldsets = (
        ("📰 Content", {
            "fields": ("title", "content", "url", "source", "author")
        }),
        ("🧠 Intelligence", {
            "fields": (
                "severity",
                "confidence_score",
                "relevance_score",
                "sentiment_score",
                "categories",
                "semantic_tags",
                "entities",
            )
        }),
        ("📌 Editorial Control", {
            "fields": (
                "is_verified",
                "requires_followup",
                "has_been_notified",
            )
        }),
        ("⚙️ System", {
            "fields": (
                "content_hash",
                "published_date",
                "scraped_date",
            )
        }),
    )

    actions = [
        "mark_as_verified",
        "force_send_notification",
        "escalate_severity",
    ]


    # ---------- Custom Display Helpers ----------

    def short_title(self, obj):
        return obj.title[:60] + "…" if len(obj.title) > 60 else obj.title
    short_title.short_description = "Title"

    def severity_badge(self, obj):
        color = {
            "low": "#16a34a",
            "medium": "#f59e0b",
            "high": "#dc2626",
        }.get(obj.severity, "#6b7280")

        return format_html(
            '<span style="color:white; background:{}; padding:4px 8px; border-radius:6px;">{}</span>',
            color,
            obj.severity.upper()
        )
    severity_badge.short_description = "Severity"

    def confidence_badge(self, obj):
        score = obj.confidence_score or 0

        if score >= 0.75:
            color = "#16a34a"
        elif score >= 0.45:
            color = "#f59e0b"
        else:
            color = "#dc2626"

        return format_html(
            '<strong style="color:{};">{:.0f}%</strong>',
            color,
            score * 100
        )
    confidence_badge.short_description = "Confidence"

    # ==========================
    # Admin Actions
    # ==========================

    @admin.action(description="✅ Mark selected items as VERIFIED")
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(
            is_verified=True,
            requires_followup=False
        )
        self.message_user(
            request,
            f"{updated} item(s) marked as verified.",
            level=messages.SUCCESS
        )

    @admin.action(description="🚨 Force-send notification (override policy)")
    def force_send_notification(self, request, queryset):
        manager = NotificationManager()
        sent = 0

        for item in queryset:
            success = manager.send_notification(
                {
                    "title": item.title,
                    "content": item.content,
                    "url": item.url,
                    "source": item.source.name,
                    "relevance_score": item.relevance_score,
                    "semantic_tags": item.semantic_tags,
                    "published_date": item.published_date,
                    "summary": item.platform_specific_data.get("summary", "")
                },
                notification_type="all"
            )

            if success:
                item.has_been_notified = True
                item.save(update_fields=["has_been_notified"])
                sent += 1

        self.message_user(
            request,
            f"🚀 Forced notifications sent for {sent} item(s).",
            level=messages.WARNING
        )

    @admin.action(description="🔥 Escalate severity (Low → Medium → High)")
    def escalate_severity(self, request, queryset):
        escalation_map = {
            "low": "medium",
            "medium": "high",
            "high": "high",
        }

        updated = 0
        for item in queryset:
            new_severity = escalation_map.get(item.severity, item.severity)
            if new_severity != item.severity:
                item.severity = new_severity
                item.requires_followup = True
                item.save(update_fields=["severity", "requires_followup"])
                updated += 1

        self.message_user(
            request,
            f"🔥 Severity escalated for {updated} item(s).",
            level=messages.ERROR
        )



# ==========================
# Semantic Patterns
# ==========================
@admin.register(SemanticPattern)
class SemanticPatternAdmin(admin.ModelAdmin):
    list_display = ("name", "pattern_type", "weight", "is_active")
    list_filter = ("pattern_type", "is_active")
    search_fields = ("name", "pattern")


# ==========================
# Notification Log
# ==========================
@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "news_item",
        "notification_type",
        "sent_to",
        "status",
        "sent_at",
    )
    list_filter = ("notification_type", "status", "sent_at")
    readonly_fields = ("sent_at", "response")
