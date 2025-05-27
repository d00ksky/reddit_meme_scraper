#!/usr/bin/env python3
"""
Test script for Reddit Meme Scraper
Run this to test your setup without starting the full scheduler
"""

import os
from dotenv import load_dotenv
from reddit_scraper import RedditScraper
from telegram_sender import TelegramSender
from utils import setup_logging, load_config

def test_scraper():
    """Test the scraper functionality"""
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Reddit Meme Scraper Test")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize components
        reddit_scraper = RedditScraper(config)
        logger.info("✅ Reddit scraper initialized")
        
        telegram_sender = TelegramSender(config)
        logger.info("✅ Telegram sender initialized")
        
        # Test scraping
        logger.info("🔍 Testing meme scraping...")
        memes = reddit_scraper.scrape_memes()
        
        if memes:
            logger.info(f"✅ Found {len(memes)} memes!")
            
            # Show meme details
            for i, meme in enumerate(memes[:3], 1):  # Show first 3 memes
                logger.info(f"  Meme {i}: {meme['title'][:50]}... (r/{meme['subreddit']}, {meme['score']} upvotes)")
            
            # Test sending (only first meme)
            logger.info("📱 Testing Telegram sending...")
            telegram_sender.send_memes([memes[0]])
            logger.info("✅ Test meme sent successfully!")
            
        else:
            logger.warning("⚠️ No memes found. Try lowering min_score in config.json")
        
        logger.info("🎉 All tests passed! Your scraper is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_scraper()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("You can now run 'python main.py' to start the full scraper.")
    else:
        print("\n❌ Test failed. Please check the logs and your configuration.")
    
    input("\nPress Enter to exit...") 