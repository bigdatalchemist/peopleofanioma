# apps/media_intelligence/aggregation/aggregator.py
import asyncio
from typing import List, Dict
import logging
from django.utils import timezone
from django.conf import settings
from apps.media_intelligence.analyzers.semantic import AniomaSemanticAnalyzer
from apps.media_intelligence.crawler.platforms import MonitorFactory
from apps.media_intelligence.models import NewsSource

logger = logging.getLogger(__name__)

class ContentAggregator:
    """Aggregate and process content from multiple sources"""
    
    def __init__(self):
        self.semantic_analyzer = AniomaSemanticAnalyzer()
        self.monitors = {}
        
    async def fetch_all_sources(self) -> List[Dict]:
        """Fetch content from all active sources"""
        all_content = []
        active_sources = NewsSource.objects.filter(is_active=True)
        logger.warning(f"[MEDIA_INTEL DEBUG] Active sources count: {active_sources.count()}")
        logger.warning(f"[MEDIA_INTEL DEBUG] Source types: {[s.source_type for s in active_sources]}")
        
        tasks = []
        for source in active_sources:
            tasks.append(self._fetch_source_content(source))
        
        # Fetch concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching source: {result}")
                continue
            if result:
                all_content.extend(result)
        
        return all_content
    
    async def _fetch_source_content(self, source: NewsSource) -> List[Dict]:
        """Fetch content from a single source"""
        try:
            platform_cfg = settings.MEDIA_INTELLIGENCE_PLATFORMS.get(source.source_type, {})
            if not platform_cfg.get("enabled", False):
                return []
            monitor = MonitorFactory.create_monitor(
                source.source_type,
                {
                    'url': source.url,
                    **source.config,
                    **platform_cfg,
                }
            )
            
            if not monitor:
                logger.warning(f"No monitor available for source type: {source.source_type}")
                return []
            
            content = await monitor.fetch_content()
            
            # Update last checked time
            source.last_checked = timezone.now()
            source.save(update_fields=['last_checked'])
            
            await monitor.close()
            
            # Add source metadata
            for item in content:
                item['source_id'] = str(source.id)
                item['source_name'] = source.name
                item['source_type'] = source.source_type
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching from source {source.name}: {e}")
            return []
    
    def process_and_filter_content(self, content_list: List[Dict]) -> List[Dict]:
        """Process content and filter for Anioma relevance"""
        relevant_items = []
        
        for item in content_list:
            try:
                # Analyze content
                analysis = self.semantic_analyzer.analyze_text(
                    item.get('content', ''),
                    item.get('title', '')
                )
                
                # Skip if not relevant
                if not analysis['is_anioma_related']:
                    continue
                
                # Enhance item with analysis results
                item.update({
                    'relevance_score': analysis['relevance_score'],
                    'is_anioma_related': analysis['is_anioma_related'],
                    'semantic_tags': analysis['semantic_tags'],
                    'detection_methods': analysis['detection_methods'],
                    'sentiment_score': analysis['sentiment'],
                    'entities': analysis['entities'],
                    'keywords_found': analysis['keywords_found']
                })
                
                relevant_items.append(item)
                
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue
        
        # Sort by relevance score
        relevant_items.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_items
    