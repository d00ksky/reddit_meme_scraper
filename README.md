# reddit_meme_scraper

_Application in development_  

Below is what I'm working on right now.

## Features

- **Configurable Sources:** Easily update the list of meme subreddits and post filters via a `.env` file.
- **Automatic Scheduling:** Fetches memes multiple times per day, scheduled using APScheduler.
- **Direct Delivery:** Sends images directly to your Telegram chat.
- **Duplicate Handling:** Prevents re-sending already seen memes.
- **Extensible:** Built with future features in mind (e.g., news summaries with OpenAI API).

## Prerequisites

- **Python 3.7+**
- **Libraries:**
  - `praw
  - `python-telegram-bot`
  - `python-dotenv`
  - `apscheduler`
- **Reddit API credentials:**  
  Create a Reddit app to get your `client_id`, `client_secret`, and set a `user_agent`.
- **Telegram Bot:**  
  Create a Telegram bot using [BotFather](https://core.telegram.org/bots#6-botfather) to obtain your bot token, and get your chat ID.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/reddit_meme_scraper.git
   cd reddit_meme_scraper
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**

   Create a `.env` file in the project root and add your credentials and settings. For example:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   
   REDDIT_CLIENT_ID=your_reddit_client_id_here
   REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
   REDDIT_USER_AGENT=your_user_agent_here
   
   # Comma-separated list of subreddits to scrape memes from
   SUBREDDITS=r/memes,r/dankmemes
   
   # Sorting method for fetching posts (hot, new, top)
   SORT_BY=hot
   
   # Number of posts to fetch per subreddit
   FETCH_COUNT=5
   
   # Scheduled times (24h format, comma-separated) when the scraper runs
   SCHEDULE_TIMES=09:00,15:00,21:00
   ```

4. **Run the Application:**

   ```bash
   python main.py
   ```

## Logging

Logs are maintained to provide insights into the scraping and messaging process. Adjust the logging configuration as needed for troubleshooting.

## Future Improvements

- Extend functionality to fetch other content types (e.g., tech news).

## Disclaimer

Use this tool responsibly and adhere to Reddit and Telegram usage guidelines.

## License

MIT License
