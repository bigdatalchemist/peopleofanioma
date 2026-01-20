# backend/apps/media_intelligence/crawler/base.py
from datetime import timedelta
from typing import Optional
import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from django.db import transaction
from django.utils import timezone

from ..models import TrackedNewsItem, NewsSource, NotificationLog
from ..aggregation.aggregator import ContentAggregator
from ..notifications.manager import NotificationManager
from ..analyzers.semantic import AniomaSemanticAnalyzer
from django.db import IntegrityError
from asgiref.sync import sync_to_async
from apps.media_intelligence.intelligence.scoring import compute_confidence_score
from apps.media_intelligence.intelligence.severity import classify_severity
from apps.media_intelligence.notifications.policy import is_notification_eligible

# Import your existing NLP tools
from apps.ethnographic_survey.utils.nlp_tools import summarize_text

logger = logging.getLogger(__name__)

class NewsCrawlerService:
    """Main service for crawling and processing news"""
    
    def __init__(self):
        self.aggregator = ContentAggregator()
        self.notification_manager = NotificationManager()
        self.semantic_analyzer = AniomaSemanticAnalyzer()
        
    async def run_crawling_cycle(self) -> Dict:
        """Run one complete crawling cycle"""
        logger.info("Starting news crawling cycle")
        
        results = {
            'total_fetched': 0,
            'relevant_found': 0,
            'new_items_stored': 0,
            'notifications_sent': 0,
            'errors': []
        }
        
        try:
            # 🔎 STEP 1 — before fetch
            logger.error("STEP 1: before fetch_all_sources")

            all_content = await self.aggregator.fetch_all_sources()

            # 🔎 STEP 2 — after fetch
            logger.error("STEP 2: after fetch_all_sources")

            results['total_fetched'] = len(all_content)

            # 🔎 STEP 3 — before semantic processing
            logger.error("STEP 3: before process_and_filter_content")

            relevant_items = await sync_to_async(
                self.aggregator.process_and_filter_content,
                thread_sensitive=True
            )(all_content)


            # 🔎 STEP 4 — after semantic processing
            logger.error("STEP 4: after process_and_filter_content")

            results['relevant_found'] = len(relevant_items)

            # 3. Deduplicate
            unique_items = self.aggregator.deduplicate_content(relevant_items)

            logger.error("STEP 5: after deduplication")

            # 4. Store + notify
            for item in unique_items:
                try:
                    saved_item = await sync_to_async(
                        self._process_and_store_item,
                        thread_sensitive=True
                    )(item)

                    if saved_item:
                        results['new_items_stored'] += 1

                        should_notify = await sync_to_async(
                            self._should_send_notification
                        )(saved_item)

                        if should_notify:
                            await self._send_notification(saved_item)
                            results['notifications_sent'] += 1

                except Exception as e:
                    error_msg = f"Error processing item {item.get('url', 'unknown')}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

            logger.error("STEP 6: end of crawling cycle")
            return results

        except Exception as e:
            logger.error("❌ CRASH BEFORE STEP COMPLETION")
            error_msg = f"Error in crawling cycle: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results

    
    def _process_and_store_item(self, item_data: Dict) -> Optional[TrackedNewsItem]:
        """Process and store a single news item"""
        
        # Check if already exists
        from apps.media_intelligence.utils.hash_utils import generate_content_hash

        title = item_data.get('title', '')
        content = item_data.get('content', '')

        content_hash = generate_content_hash(title, content)
        confidence_score = compute_confidence_score(item_data)
        severity = classify_severity(item_data)

        # Strong deduplication (authoritative)
        if TrackedNewsItem.objects.filter(content_hash=content_hash).exists():
            return None

        
        try:
            source = NewsSource.objects.get(id=item_data['source_id'])
        except NewsSource.DoesNotExist:
            logger.error(f"Source not found: {item_data['source_id']}")
            return None
        
        # Apply your existing NLP tools
        full_text = f"{item_data.get('title', '')} {item_data.get('content', '')}"
        
        # Generate summary using your existing function
        summary = summarize_text(full_text, max_length=150, min_length=50)
        
        # Keywords intentionally left empty (future enrichment hook)
        keywords = []
        
        # Create the news item
        try:
            with transaction.atomic():
                news_item = TrackedNewsItem.objects.create(
                    source=source,
                    title=item_data.get('title', '')[:500],
                    content=item_data.get('content', '')[:10000],
                    url=item_data.get('url', ''),
                    author=item_data.get('author', ''),
                    published_date=item_data.get('published_date', timezone.now()),
                    
                    # Semantic analysis results
                    categories=item_data.get('detection_methods', []),
                    keywords=keywords,
                    entities=item_data.get('entities', {}),
                    sentiment_score=item_data.get('sentiment_score', 0.0),
                    relevance_score=item_data.get('relevance_score', 0.0),
                    is_anioma_related=item_data.get('is_anioma_related', False),
                    semantic_tags=item_data.get('semantic_tags', []),
                    content_hash=content_hash,
                    is_processed=False,
                    confidence_score=confidence_score,
                    severity=severity,

                    # Store summary in platform_specific_data
                    platform_specific_data={
                        **item_data.get('platform_specific_data', {}),
                        'summary': summary,
                    }
                )
            logger.info(f"Stored new item: {news_item.title[:100]}")
            return news_item
        except IntegrityError:
            return None
        

    def _should_send_notification(self, news_item: TrackedNewsItem) -> bool:
        """Determine if notification should be sent"""
        
        # Don't send if already notified
        if news_item.has_been_notified:
            return False
        
        # ❌ Policy gate check
        if not is_notification_eligible(news_item):
            logger.info(
            f"Policy block | "
            f"relevance={news_item.relevance_score} "
            f"confidence={news_item.confidence_score} "
            f"severity={news_item.severity}"
        )
            return False
        
        # 🔥 BREAKING NEWS OVERRIDE
        if news_item.severity == "high":
            logger.info("🔥 Breaking-news override triggered")
            return True
        
        # ❌ Rate limiting (anti-burnout)
        last_hour = timezone.now() - timedelta(hours=1)
        recent_notifications = NotificationLog.objects.filter(
            sent_at__gte=last_hour
        ).count()
        
        if recent_notifications >= 5:  # Limit to 5 per hour
            logger.info("Notification rate limit reached")
            return False
        
        return True
    
    async def _send_notification(self, news_item: TrackedNewsItem):
        """Send notification for a news item"""
        try:
            # Prepare notification data
            notification_data = {
                'title': news_item.title,
                'content': news_item.content[:500],
                'url': news_item.url,
                'source': news_item.source.name,
                'relevance_score': news_item.relevance_score,
                'semantic_tags': news_item.semantic_tags,
                'published_date': news_item.published_date,
                'summary': news_item.platform_specific_data.get('summary', ''),
                "severity": news_item.severity,
            }
            
            # Send notification
            success = self.notification_manager.send_notification(
                notification_data,
                notification_type='all'  # or specify which channels
            )
            
            if success:
                # Mark as notified
                news_item.has_been_notified = True
                news_item.save(update_fields=['has_been_notified'])
                
                # Log notification
                NotificationLog.objects.create(
                    news_item=news_item,
                    notification_type='alert',
                    sent_to='user',  # Could be email address, phone number, etc.
                    status='sent',
                    response={'success': True}
                )
                
                logger.info(f"Notification sent for: {news_item.title[:100]}")
            else:
                logger.error(f"Failed to send notification for: {news_item.title[:100]}")
                
        except Exception as e:
            logger.error(f"Error in notification process: {e}")