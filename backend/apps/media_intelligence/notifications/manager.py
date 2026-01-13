# backend/apps/media_intelligence/notifications/manager.py
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import sys
import os

from backend.apps.media_intelligence.intelligence import severity

# Add Django to path if needed
try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("Note: Django settings not available")

logger = logging.getLogger(__name__)


class NotificationManager:
    """Simplified notification manager for initial testing"""
    
    def __init__(self):
        self.config = self._load_config()
        logger.info("NotificationManager initialized")
    
    def _load_config(self):
        """Load configuration from Django settings or defaults"""
        config = {
            'notification': {
                'email': {
                    'enabled': False,
                    'host': 'localhost',
                    'port': 1025,
                    'username': '',
                    'password': '',
                    'from_email': 'tracker@anioma.org',
                    'to_email': 'test@example.com',
                },
                'console': {
                    'enabled': True,
                }
            }
        }
        
        # Try to get from Django settings
        if DJANGO_AVAILABLE:
            try:
                django_config = getattr(settings, 'NEWS_TRACKER_CONFIG', {})
                config.update(django_config)
                logger.info("Loaded config from Django settings")
            except Exception as e:
                logger.warning(f"Could not load Django config: {e}")
        
        return config
    
    def send_notification(self, news_item: Dict, notification_type: str = 'console') -> bool:
        """
        Send notification about a news item
        
        Args:
            news_item: Dictionary containing news item data
            notification_type: 'console', 'email', 'all'
        
        Returns:
            bool: True if notification was sent successfully
        """
        success = True
        
        try:
            # Prepare notification message
            message = self._prepare_message(news_item)
            
            # Send based on type
            if notification_type in ['all', 'console']:
                if self.config.get('notification', {}).get('console', {}).get('enabled', True):
                    success = success and self._send_console(message, news_item)
            
            if notification_type in ['all', 'email']:
                email_config = self.config.get('notification', {}).get('email', {})
                if email_config.get('enabled', False):
                    success = success and self._send_email(message, news_item, email_config)
            
            # Try other channels if configured
            if notification_type == 'all':
                success = success and self._try_other_channels(message, news_item)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def _prepare_message(self, news_item: Dict) -> str:
        """Prepare formatted notification message"""
        title = news_item.get('title', 'Untitled')
        content = news_item.get('content', '')[:200]
        url = news_item.get('url', '#')
        relevance = news_item.get('relevance_score', 0)
        source = news_item.get('source', 'Unknown')
        severity = news_item.get("severity", "unknown")
        prefix = "🔥 BREAKING NEWS" if severity == "high" else "📢 News Update"

        
        message = f"""
{prefix}


**Title:** {title}

**Source:** {source}
**Relevance Score:** {relevance:.2%}

**Snippet:**
{content}...

**Read More:** {url}

---
Detected by Anioma News Tracker
"""
        return message
    
    def _send_console(self, message: str, news_item: Dict) -> bool:
        """Send notification to console"""
        try:
            print("\n" + "="*60)
            print("📢 NEWS TRACKER NOTIFICATION")
            print("="*60)
            print(message)
            print("="*60 + "\n")
            
            logger.info(f"Console notification sent for: {news_item.get('title', '')[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending console notification: {e}")
            return False
    
    def _send_email(self, message: str, news_item: Dict, config: Dict) -> bool:
        """Send email notification"""
        try:
            # Check if config is complete
            if not all(k in config for k in ['host', 'port', 'from_email', 'to_email']):
                logger.warning("Email configuration incomplete, using console instead")
                return self._send_console(f"[EMAIL FALLBACK] {message}", news_item)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Anioma News Alert: {news_item.get('title', '')[:50]}..."
            msg['From'] = config['from_email']
            msg['To'] = config['to_email']
            
            # Add text and HTML versions
            msg.attach(MIMEText(message, 'plain'))
            
            # Try to send
            if config['host'] == 'localhost' and config['port'] == 1025:
                # Use local test server
                with smtplib.SMTP(config['host'], config['port']) as server:
                    server.send_message(msg)
                logger.info(f"Email sent via local server for: {news_item.get('title', '')[:50]}")
            else:
                # For real email servers
                with smtplib.SMTP(config['host'], config['port']) as server:
                    server.starttls()
                    if config.get('username') and config.get('password'):
                        server.login(config['username'], config['password'])
                    server.send_message(msg)
                logger.info(f"Email sent via {config['host']} for: {news_item.get('title', '')[:50]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            # Fallback to console
            self._send_console(f"[EMAIL FAILED - {e}] {message}", news_item)
            return False
    
    def _try_other_channels(self, message: str, news_item: Dict) -> bool:
        """Try other notification channels if configured"""
        success = True
        
        # Try Telegram if configured
        telegram_config = self.config.get('notification', {}).get('telegram', {})
        if telegram_config.get('enabled', False):
            try:
                import telegram
                bot_token = telegram_config.get('bot_token')
                chat_id = telegram_config.get('chat_id')
                
                if bot_token and chat_id:
                    bot = telegram.Bot(token=bot_token)
                    bot.send_message(
                        chat_id=chat_id,
                        text=message,
                    )
                    logger.info(f"Telegram notification sent")
                else:
                    logger.warning("Telegram configured but missing bot_token or chat_id")
                    
            except ImportError:
                logger.warning("python-telegram-bot not installed")
            except Exception as e:
                logger.error(f"Error sending Telegram: {e}")
                success = False
        
        # Try Twilio if configured
        twilio_config = self.config.get('notification', {}).get('twilio', {})
        if twilio_config.get('enabled', False):
            try:
                from twilio.rest import Client
                
                if all(k in twilio_config for k in ['account_sid', 'auth_token', 'from_number', 'to_number']):
                    client = Client(twilio_config['account_sid'], twilio_config['auth_token'])
                    
                    client.messages.create(
                        body=message[:1600],  # SMS length limit
                        from_=twilio_config['from_number'],
                        to=twilio_config['to_number']
                    )
                    logger.info(f"SMS notification sent")
                else:
                    logger.warning("Twilio configured but missing credentials")
                    
            except ImportError:
                logger.warning("twilio not installed")
            except Exception as e:
                logger.error(f"Error sending SMS: {e}")
                success = False
        
        return success


# Simple test function
def test_notification():
    """Test the notification system"""
    manager = NotificationManager()
    
    test_item = {
        'title': 'Test: Anioma Cultural Festival Announced',
        'content': 'The annual Anioma cultural festival will take place in Asaba next month...',
        'url': 'https://example.com/news/1',
        'source': 'Test Source',
        'relevance_score': 0.85,
        'semantic_tags': ['cultural', 'festival', 'asaba']
    }
    
    print("Testing notification system...")
    result = manager.send_notification(test_item, 'console')
    
    if result:
        print("✅ Notification test passed!")
    else:
        print("❌ Notification test failed!")
    
    return result


if __name__ == '__main__':
    test_notification()