#!/usr/bin/env python3
"""
Reddit Meme Scraper
A tool to scrape memes from Reddit and send them via Telegram
"""

import os
import json
import time
import schedule
from dotenv import load_dotenv

from reddit_scraper import RedditScraper
from telegram_sender import TelegramSender
from monitoring import MonitoringManager
from utils import setup_logging, load_config

def main():
    """Main function to run the meme scraper"""
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Reddit Meme Scraper")
    
    # Load configuration
    config = load_config()
    
    # Initialize components
    reddit_scraper = RedditScraper(config)
    telegram_sender = TelegramSender(config)
    monitor = MonitoringManager(config)
    
    # Send startup notification
    monitor.send_webhook_notification("🚀 Meme scraper started successfully")
    
    def scrape_and_send():
        """Function to scrape memes and send them"""
        try:
            logger.info("Starting meme scraping session")
            
            # Scrape memes from Reddit
            memes = reddit_scraper.scrape_memes()
            
            if memes:
                logger.info(f"Found {len(memes)} new memes")
                monitor.update_stats('scraped', count=len(memes))
                
                # Send memes via Telegram
                sent_count = 0
                failed_count = 0
                
                for meme in memes:
                    try:
                        telegram_sender.send_memes([meme])
                        sent_count += 1
                        monitor.update_stats('sent', count=1)
                    except Exception as e:
                        failed_count += 1
                        monitor.update_stats('failed', count=1, error=e)
                        logger.error(f"Failed to send meme: {e}")
                
                logger.info(f"Sent {sent_count} memes successfully, {failed_count} failed")
                
                # Send notification for significant events
                if failed_count > 0:
                    monitor.send_webhook_notification(
                        f"⚠️ Sent {sent_count}/{len(memes)} memes. {failed_count} failed.", 
                        'warning'
                    )
                elif sent_count > 0:
                    monitor.send_webhook_notification(f"✅ Successfully sent {sent_count} memes")
            else:
                logger.info("No new memes found")
            
            monitor.update_stats('run_complete')
                
        except Exception as e:
            logger.error(f"Error in scrape_and_send: {e}")
            monitor.update_stats('failed', count=1, error=e)
            monitor.send_webhook_notification(f"❌ Scraping failed: {str(e)[:100]}...", 'error')
    
    # Schedule the job
    interval_hours = config.get('schedule', {}).get('interval_hours', 1)
    schedule.every(interval_hours).hours.do(scrape_and_send)
    
    logger.info(f"Scheduler set up to run every {interval_hours} hour(s)")
    
    # Run once immediately
    scrape_and_send()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 