# peopleofanioma/backend/apps/media_intelligence/management/commands/run_media_intelligence.py
from django.core.management.base import BaseCommand
import asyncio
import logging
from apps.media_intelligence.crawler.base import NewsCrawlerService
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Anioma news tracker pipeline'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run in continuous mode (keep checking)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Interval in minutes between checks (continuous mode only)'
        )
    
    def handle(self, *args, **options):
        import os

        ENV = os.getenv("DJANGO_ENV", "development")

        if options["continuous"] and ENV == "production":
            self.stdout.write(
                self.style.ERROR(
                    "❌ Continuous mode is disabled in production. Use cron scheduling instead."
                )
            )
            return

        continuous = options['continuous']
        interval = options['interval'] * 60  # Convert to seconds
        
        self.stdout.write(self.style.SUCCESS(
            f'🚀 Starting Anioma News Tracker Pipeline'
        ))
        
        if continuous:
            self.stdout.write(self.style.WARNING(
                f'Running in continuous mode (checking every {interval/60} minutes)'
            ))
            asyncio.run(self.run_continuously(interval))
        else:
            asyncio.run(self.run_once())
    
    async def run_once(self):
        """Run a single crawling cycle"""
        try:
            service = NewsCrawlerService()
            results = await service.run_crawling_cycle()
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Crawling completed:'
            ))
            self.stdout.write(f'   Total fetched: {results["total_fetched"]}')
            self.stdout.write(f'   Relevant found: {results["relevant_found"]}')
            self.stdout.write(f'   New items stored: {results["new_items_stored"]}')
            self.stdout.write(f'   Notifications sent: {results["notifications_sent"]}')
            
            if results['errors']:
                self.stdout.write(self.style.ERROR(
                    f'   Errors: {len(results["errors"])}'
                ))
                for error in results['errors'][:3]:  # Show first 3 errors
                    self.stdout.write(f'     - {error}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
    
    async def run_continuously(self, interval: int):
        """Run crawling continuously with specified interval"""
        import asyncio
        
        service = NewsCrawlerService()
        
        while True:
            try:
                self.stdout.write(self.style.SUCCESS(
                    f'\n🔄 Starting crawling cycle at {timezone.now()}'
                ))
                
                results = await service.run_crawling_cycle()
                
                self.stdout.write(f'   Results: {results["new_items_stored"]} new items')
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\n👋 Stopping news tracker...'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in continuous run: {e}'))
                await asyncio.sleep(60)  # Wait a minute before retrying