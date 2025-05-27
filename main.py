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
    
    def scrape_and_send():
        """Function to scrape memes and send them"""
        try:
            logger.info("Starting meme scraping session")
            
            # Scrape memes from Reddit
            memes = reddit_scraper.scrape_memes()
            
            if memes:
                logger.info(f"Found {len(memes)} new memes")
                
                # Send memes via Telegram
                telegram_sender.send_memes(memes)
                
                logger.info(f"Sent {len(memes)} memes successfully")
            else:
                logger.info("No new memes found")
                
        except Exception as e:
            logger.error(f"Error in scrape_and_send: {e}")
    
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