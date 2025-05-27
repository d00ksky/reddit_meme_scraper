# Reddit Meme Scraper

🎭 **Your Personal Meme Delivery Service**

A Python bot that scrapes fresh memes from Reddit and delivers them directly to your Telegram! Perfect for staying updated with the latest memes without getting distracted by social media.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Easy Setup
```bash
python setup.py
```
This interactive setup will guide you through:
- Creating Reddit API credentials
- Setting up a Telegram bot
- Testing your configuration

### 3. Run the Scraper
```bash
python main.py
```

## 📋 Manual Setup (If you prefer)

### Reddit API Setup
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as app type
4. Set redirect URI to: `http://localhost:8080`
5. Note your `client_id` and `client_secret`

### Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Message your bot to start a chat
5. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

### Create .env file
```bash
# Copy from env_example.txt and fill in your credentials
cp env_example.txt .env
```

## ⚙️ Configuration

Edit `config.json` to customize your meme preferences:

```json
{
    "reddit": {
        "subreddits": ["dankmemes", "memes", "funny", "wholesomememes"],
        "sort_by": "hot",           // "hot", "new", "top"
        "limit": 10,                // Number of posts to check per subreddit
        "min_score": 100            // Minimum upvotes required
    },
    "schedule": {
        "interval_hours": 1         // How often to check for new memes
    },
    "filters": {
        "image_only": true,         // Only send image posts
        "exclude_nsfw": true,       // Filter out NSFW content
        "max_title_length": 200     // Maximum title length
    }
}
```

## 🎯 Features

- ✅ **Smart Filtering**: Only high-quality memes based on upvotes and content type
- ✅ **Duplicate Prevention**: Never sends the same meme twice
- ✅ **Multiple Subreddits**: Scrapes from your favorite meme communities
- ✅ **Scheduled Delivery**: Automatic hourly (or custom interval) updates
- ✅ **Telegram Integration**: Beautiful formatted messages with meme info
- ✅ **Error Handling**: Robust fallbacks for different image types
- ✅ **Configurable**: Easy JSON configuration for all settings
- ✅ **Logging**: Detailed logs for monitoring and debugging

## 📱 Telegram Message Format

Each meme comes with:
- 🖼️ **High-quality image**
- 📝 **Meme title**
- 📍 **Source subreddit**
- ⬆️ **Upvote count**
- 👤 **Original author**
- 🔗 **Direct Reddit link**

## 🔧 Advanced Usage

### Run Once (Test Mode)
```bash
python -c "
from main import main
from dotenv import load_dotenv
load_dotenv()
from reddit_scraper import RedditScraper
from telegram_sender import TelegramSender
from utils import load_config

config = load_config()
scraper = RedditScraper(config)
sender = TelegramSender(config)
memes = scraper.scrape_memes()
sender.send_memes(memes)
"
```

### Custom Subreddits
Add any image-based subreddits to the config:
```json
"subreddits": ["dankmemes", "memes", "ProgrammerHumor", "wholesomememes", "funny"]
```

### Scheduling Options
- **Hourly**: `"interval_hours": 1`
- **Every 30 minutes**: `"interval_hours": 0.5`
- **Daily**: `"interval_hours": 24`

## 📁 Project Structure

```
reddit_meme_scraper/
├── main.py              # Main application entry point
├── reddit_scraper.py    # Reddit API integration
├── telegram_sender.py   # Telegram bot functionality
├── utils.py            # Helper functions
├── setup.py            # Interactive setup script
├── config.json         # Configuration settings
├── requirements.txt    # Python dependencies
├── .env               # Your API credentials (created by setup)
└── sent_posts.json    # Tracks sent memes (auto-created)
```

## 🐛 Troubleshooting

### Common Issues

**"Reddit API test failed"**
- Check your Reddit credentials in `.env`
- Ensure you selected "script" type when creating the Reddit app

**"Telegram bot test failed"**
- Verify your bot token is correct
- Make sure you've messaged your bot at least once
- Double-check your chat ID

**"No memes found"**
- Lower the `min_score` in config.json
- Check if the subreddits are image-based
- Try changing `sort_by` to "new" or "top"

## 🎓 Perfect for Learning

This project demonstrates:
- **API Integration** (Reddit + Telegram)
- **Web Scraping** with PRAW
- **Async Programming** for Telegram
- **Configuration Management**
- **Error Handling & Logging**
- **Task Scheduling**
- **Data Persistence**

## 📜 License

MIT License - feel free to modify and share!
