#!/usr/bin/env python3
"""
Setup script for Reddit Meme Scraper
Helps you get API credentials and test the setup
"""

import os
import json
from dotenv import load_dotenv

def create_env_file():
    """Create .env file from user input"""
    print("🚀 Reddit Meme Scraper Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("📁 .env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 We need to collect your API credentials...")
    print("\n1️⃣  REDDIT API SETUP:")
    print("   • Go to: https://www.reddit.com/prefs/apps")
    print("   • Click 'Create App' or 'Create Another App'")
    print("   • Choose 'script' as app type")
    print("   • Set redirect URI to: http://localhost:8080")
    print("   • Note down your client_id and client_secret")
    
    reddit_client_id = input("\n🔑 Enter Reddit Client ID: ").strip()
    reddit_client_secret = input("🔑 Enter Reddit Client Secret: ").strip()
    reddit_username = input("👤 Enter your Reddit username: ").strip()
    
    print("\n2️⃣  TELEGRAM BOT SETUP:")
    print("   • Open Telegram and message @BotFather")
    print("   • Send /newbot and follow the instructions")
    print("   • Copy the bot token")
    print("   • Message your bot to start a chat")
    print("   • Get your chat ID by messaging @userinfobot")
    
    telegram_bot_token = input("\n🤖 Enter Telegram Bot Token: ").strip()
    telegram_chat_id = input("💬 Enter your Telegram Chat ID: ").strip()
    
    # Create .env file
    env_content = f"""# Reddit API Credentials
REDDIT_CLIENT_ID={reddit_client_id}
REDDIT_CLIENT_SECRET={reddit_client_secret}
REDDIT_USER_AGENT=RedditMemeScraper/1.0 by {reddit_username}

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN={telegram_bot_token}
TELEGRAM_CHAT_ID={telegram_chat_id}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    return True

def test_setup():
    """Test if the setup works"""
    print("\n🧪 Testing setup...")
    
    load_dotenv()
    
    # Test Reddit credentials
    try:
        import praw
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Test by getting a subreddit
        test_subreddit = reddit.subreddit('memes')
        test_subreddit.display_name  # This will fail if credentials are wrong
        print("✅ Reddit API connection successful!")
        
    except Exception as e:
        print(f"❌ Reddit API test failed: {e}")
        return False
    
    # Test Telegram credentials
    try:
        from telegram import Bot
        import asyncio
        
        async def test_telegram():
            bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            await bot.send_message(
                chat_id=chat_id,
                text="🎉 Reddit Meme Scraper setup successful!\n\nYour meme delivery service is ready!"
            )
        
        asyncio.run(test_telegram())
        print("✅ Telegram bot test successful!")
        
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your scraper is ready to use.")
    print("💡 Run 'python main.py' to start scraping memes!")
    return True

def main():
    """Main setup function"""
    if create_env_file():
        test_setup()

if __name__ == "__main__":
    main() 