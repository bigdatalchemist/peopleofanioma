import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import importlib
from django.conf import settings

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
    
    async def fetch_content(self) -> List[Dict]:
        """Fetch content from the platform"""
        raise NotImplementedError
    
    def parse_content(self, raw_content) -> List[Dict]:
        """Parse raw content into structured format"""
        raise NotImplementedError
    
    async def close(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

class WebsiteMonitor(BaseMonitor):
    """Monitor websites and blogs"""
    
    async def fetch_content(self) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; AniomaNewsTracker/1.0)'
                }
                
                async with session.get(self.config['url'], headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self.parse_content(html)
                    else:
                        logger.error(f"Failed to fetch {self.config['url']}: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching website {self.config['url']}: {e}")
            return []
    
    def parse_content(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Look for article elements (customize based on website structure)
        article_elements = soup.find_all(['article', 'div.article', 'div.post', 'div.blog-post'])
        
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
    
    async def fetch_content(self) -> List[Dict]:
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

class RedditMonitor(BaseMonitor):
    """Monitor Reddit for discussions"""
    
    def __init__(self, source_config: Dict):
        super().__init__(source_config)
        self.reddit = self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Initialize Reddit API"""
        praw = safe_import("praw")
        if not praw:
            return None
        
        if not self.config.get("client_id"):
            logger.warning("[Media Intelligence] Reddit credentials missing.")
            return None

        try:
            reddit = praw.Reddit(
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                user_agent="AniomaNewsTracker/1.0"
            )
            return reddit
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            return None
    
    async def fetch_content(self) -> List[Dict]:
        if not self.reddit:
            return []
        
        try:
            posts = []
            subreddit_name = self.config.get('subreddit', 'all')
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for submission in subreddit.new(limit=50):
                posts.append({
                    'title': submission.title,
                    'content': submission.selftext,
                    'url': f"https://reddit.com{submission.permalink}",
                    'published_date': datetime.fromtimestamp(submission.created_utc),
                    'author': str(submission.author),
                    'platform_specific_data': {
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'num_comments': submission.num_comments
                    }
                })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Reddit content: {e}")
            return []

class FacebookMonitor(BaseMonitor):
    """Monitor Facebook pages and groups"""
    
    async def fetch_content(self) -> List[Dict]:
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

class YouTubeMonitor(BaseMonitor):
    """Monitor YouTube for relevant videos"""
    
    async def fetch_content(self) -> List[Dict]:
        try:
            # YouTube Data API v3 integration
            discovery = safe_import("googleapiclient.discovery")
            if not discovery:
                return []
            
            if not self.config.get("api_key"):
                logger.warning("[Media Intelligence] YouTube API key missing.")
                return []

            
            api_key = self.config.get('api_key')
            channel_id = self.config.get('channel_id')
            
            if not api_key or not channel_id:
                return []
            
            youtube = discovery.build("youtube", "v3", developerKey=api_key)
            
            # Get channel uploads playlist
            request = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return []
            
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from playlist
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=50
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                snippet = item['snippet']
                videos.append({
                    'title': snippet['title'],
                    'content': snippet['description'],
                    'url': f"https://youtube.com/watch?v={snippet['resourceId']['videoId']}",
                    'published_date': snippet['publishedAt'],
                    'author': snippet['channelTitle'],
                    'platform_specific_data': {
                        'video_id': snippet['resourceId']['videoId'],
                        'channel_id': channel_id
                    }
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching YouTube content: {e}")
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
            "website": WebsiteMonitor,
            "twitter": TwitterMonitor,
            "facebook": FacebookMonitor,
            "reddit": RedditMonitor,
            "youtube": YouTubeMonitor,
        }

        monitor_class = monitors.get(source_type)

        if not monitor_class:
            logger.warning(
                f"[Media Intelligence] No monitor implementation for '{source_type}'."
            )
            return None

        return monitor_class(config)
