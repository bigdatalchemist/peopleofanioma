# backend/apps/media_intelligence/crawler/platforms.py
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import importlib
from django.conf import settings
from apps.media_intelligence.constants import SourceType
import feedparser


logger = logging.getLogger(__name__)

def safe_import(module_name: str):
    """
    Safely import an optional dependency.
    Returns the module or None if not installed.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        logger.warning(
            f"[Media Intelligence] Optional dependency '{module_name}' not installed."
        )
        return None



class BaseMonitor:
    """Base class for all platform monitors"""
    
    def __init__(self, source_config: Dict):
        self.config = source_config
        self.session = None
    
    def fetch_content(self) -> List[Dict]:
        """Fetch content from the platform"""
        raise NotImplementedError
    
    def parse_content(self, raw_content) -> List[Dict]:
        """Parse raw content into structured format"""
        raise NotImplementedError
    
    def close(self):
        """Cleanup resources"""
        if self.session:
            self.session.close()

class WebsiteMonitor(BaseMonitor):
    """Monitor websites and blogs"""
    
    def fetch_content(self) -> List[Dict]:
        try:
            url = self.config["url"]

            # Otherwise treat as HTML
            with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (AniomaNewsTracker/1.0)"
                }
                with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = response.text()
                        return self.parse_content(html)
                    else:
                        logger.error(f"Failed to fetch {url}: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error fetching website {self.config.get('url')}: {e}")
            return []

    
    def parse_content(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Look for article elements (customize based on website structure)
        article_elements = soup.find_all("article") or soup.find_all("a", href=True)

        
        for element in article_elements:
            try:
                # Extract title
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                title = title_elem.text.strip() if title_elem else ""
                
                # Extract content
                content_elem = element.find(['div.content', 'div.entry-content', 'article-content'])
                content = content_elem.text.strip() if content_elem else ""
                
                # Extract link
                link_elem = element.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = self.config['url'].rstrip('/') + '/' + link.lstrip('/')
                
                # Extract date
                date_elem = element.find(['time', 'span.date', 'div.date'])
                date_text = date_elem.text.strip() if date_elem else ""
                published_date = self._parse_date(date_text)
                
                if title and content:
                    articles.append({
                        'title': title,
                        'content': content[:5000],  # Limit content length
                        'url': link,
                        'published_date': published_date,
                        'author': self._extract_author(element),
                        'raw_html': str(element)[:10000]  # Store for debugging
                    })
                    
            except Exception as e:
                logger.error(f"Error parsing article element: {e}")
                continue
        
        return articles
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse various date formats"""
        try:
            # Add date parsing logic based on common formats
            # This is simplified - you might need more robust parsing
            return datetime.now()
        except:
            return datetime.now()
    
    def _extract_author(self, element) -> str:
        """Extract author from element"""
        author_elem = element.find(['span.author', 'div.author', 'a.author'])
        return author_elem.text.strip() if author_elem else ""
    


class RSSMonitor(BaseMonitor):
    def fetch_content(self) -> List[Dict]:
        try:
            feed = feedparser.parse(self.config["url"])
            items = []

            for entry in feed.entries[:20]:
                items.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published_date": datetime.now(),
                    "author": entry.get("source", {}).get("title", ""),
                    "platform_specific_data": {
                        "source": "google_news",
                        "platform_hint": self.config.get("platform_hint"),
                    },
                })

            return items

        except Exception as e:
            logger.error(f"RSS fetch error: {e}")
            return []




class TwitterMonitor(BaseMonitor):
    """Monitor Twitter/X for mentions"""
    
    def __init__(self, source_config: Dict):
        super().__init__(source_config)
        self.api = self._initialize_twitter_api()
    
    def _initialize_twitter_api(self):
        """Initialize Twitter API v2"""
        # You'll need to set up Twitter API credentials
        tweepy = safe_import("tweepy")
        if not tweepy:
            return None
        
        if not self.config.get("bearer_token"):
            logger.warning("[Media Intelligence] Twitter bearer token missing.")
            return None
        
        try:
            return tweepy.Client(
                bearer_token=self.config.get('bearer_token'),
                consumer_key=self.config.get('consumer_key'),
                consumer_secret=self.config.get('consumer_secret'),
                access_token=self.config.get('access_token'),
                access_token_secret=self.config.get('access_token_secret'),
                wait_on_rate_limit=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            return None
    
    def fetch_content(self) -> List[Dict]:
        if not self.api:
            return []
        
        try:
            tweets = []
            search_query = self.config.get('search_query', '')
            
            # Search for tweets
            response = self.api.search_recent_tweets(
                query=search_query,
                max_results=100,
                tweet_fields=['created_at', 'author_id', 'text', 'entities'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if response.data:
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    user = users.get(tweet.author_id)
                    tweets.append({
                        'title': f"Tweet by {user.username if user else 'Unknown'}",
                        'content': tweet.text,
                        'url': f"https://twitter.com/i/web/status/{tweet.id}",
                        'published_date': tweet.created_at,
                        'author': user.username if user else 'Unknown',
                        'platform_specific_data': {
                            'tweet_id': tweet.id,
                            'author_id': tweet.author_id,
                            'retweet_count': tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'like_count': tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0
                        }
                    })
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching Twitter content: {e}")
            return []
        
class TikTokMonitor(BaseMonitor):
    """Monitor TikTok accounts or hashtag pages"""

    def fetch_content(self) -> List[Dict]:
        try:
            posts = []

            username = self.config.get("username")
            hashtag = self.config.get("hashtag")

            # Choose ONE strategy per source
            if not username and not hashtag:
                logger.warning("[Media Intelligence] TikTok source missing username or hashtag.")
                return []

            # Lazy import (prevents memory crash if lib missing)
            tiktokapi = safe_import("tiktokapipy")
            if not tiktokapi:
                return []

            # ⚠️ Placeholder logic — TikTok scraping is fragile
            # Replace with your chosen lib’s real calls
            videos = []  # fetched videos go here

            for video in videos[:20]:
                posts.append({
                    "title": video.get("desc", "")[:200],
                    "content": video.get("desc", ""),
                    "url": video.get("share_url", ""),
                    "published_date": video.get("create_time", datetime.now()),
                    "author": video.get("author", username or hashtag),
                    "platform_specific_data": {
                        "likes": video.get("like_count", 0),
                        "comments": video.get("comment_count", 0),
                        "shares": video.get("share_count", 0),
                        "platform": "tiktok",
                    },
                })

            return posts

        except Exception as e:
            logger.error(f"Error fetching TikTok content: {e}")
            return []
        

class FacebookMonitor(BaseMonitor):
    """Monitor Facebook pages and groups"""
    
    def fetch_content(self) -> List[Dict]:
        try:
            # Note: Facebook scraping requires careful handling due to terms of service
            # Consider using official API if possible
            posts = []
            page_name = self.config.get('page_name')
            
            if page_name:
                # Using facebook-scraper library (install: pip install facebook-scraper)
                facebook_scraper = safe_import("facebook_scraper")
                if not facebook_scraper:
                    return []
                
                if not self.config.get("access_token"):
                    logger.warning("[Media Intelligence] Facebook access token missing.")
                    return []
                
                get_posts = facebook_scraper.get_posts
                
                for post in get_posts(page_name, pages=3):
                    posts.append({
                        'title': post.get('text', '')[:200],
                        'content': post.get('text', ''),
                        'url': post.get('post_url', ''),
                        'published_date': post.get('time', datetime.now()),
                        'author': page_name,
                        'platform_specific_data': {
                            'likes': post.get('likes', 0),
                            'comments': post.get('comments', 0),
                            'shares': post.get('shares', 0)
                        }
                    })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Facebook content: {e}")
            return []



class MonitorFactory:
    """Factory to create policy-governed platform monitors"""

    @staticmethod
    def create_monitor(source_type: str, config: Dict) -> Optional[BaseMonitor]:
        source_type = source_type.lower()

        platform_policy = getattr(
            settings,
            "MEDIA_INTELLIGENCE_PLATFORMS",
            {}
        )

        platform_config = platform_policy.get(source_type)

        # Platform not declared at all
        if not platform_config:
            logger.info(
                f"[Media Intelligence] Platform '{source_type}' not configured."
            )
            return None

        # Platform explicitly disabled
        if not platform_config.get("enabled", False):
            logger.info(
                f"[Media Intelligence] Platform '{source_type}' disabled by policy."
            )
            return None

        # Dependency enforcement
        for dependency in platform_config.get("requires", []):
            if not safe_import(dependency):
                logger.warning(
                    f"[Media Intelligence] Platform '{source_type}' disabled — missing dependency '{dependency}'."
                )
                return None

        monitors = {
            SourceType.WEBSITE: WebsiteMonitor,
            SourceType.TWITTER: TwitterMonitor,
            SourceType.FACEBOOK: FacebookMonitor,
            SourceType.TIKTOK: TikTokMonitor,
            SourceType.RSS: RSSMonitor,
        }

        monitor_class = monitors.get(source_type)

        if not monitor_class:
            logger.warning(
                f"[Media Intelligence] No monitor implementation for '{source_type}'."
            )
            return None

        return monitor_class(config)
