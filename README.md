# Reddit Meme Scraper

🎭 **Your Personal Meme Delivery Service**

A Python application that scrapes memes from Reddit and sends them via Telegram. This tool automatically collects memes from specified subreddits and forwards them to your Telegram channel or chat.

## Features

- Scrapes memes from multiple subreddits
- Sends memes via Telegram bot
- Configurable scheduling
- Automatic duplicate detection
- Logging system for monitoring
- Cross-platform support (Windows, Linux)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Reddit API credentials
- Telegram Bot Token

## Installation

### Windows

1. **Install Python**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/reddit_meme_scraper.git
   cd reddit_meme_scraper
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   - Create a `.env` file in the project root
   - Add your credentials:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=your_user_agent
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

### Fedora

1. **Install Python and Git**
   ```bash
   sudo dnf update
   sudo dnf install python3 python3-pip python3-venv git
   ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/reddit_meme_scraper.git
   cd reddit_meme_scraper
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   - Create a `.env` file in the project root
   - Add your credentials (same as Windows section)

### Ubuntu

1. **Install Python and Git**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/reddit_meme_scraper.git
   cd reddit_meme_scraper
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   - Create a `.env` file in the project root
   - Add your credentials (same as Windows section)

## Configuration

1. **Reddit API Setup**
   - Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Click "Create App" or "Create Another App"
   - Fill in the required information
   - Note down the client ID and client secret

2. **Telegram Bot Setup**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot using `/newbot`
   - Note down the bot token
   - Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

3. **Configure `config.json`**
   ```json
   {
     "subreddits": ["memes", "dankmemes"],
     "schedule": {
       "interval_hours": 1
     },
     "telegram": {
       "max_memes_per_batch": 5
     }
   }
   ```

## Usage

### Windows

1. **Run the Application**
   ```bash
   .\venv\Scripts\python main.py
   ```

2. **Run as Windows Service (Optional)**
   - Install NSSM (Non-Sucking Service Manager)
   - Create a service:
   ```bash
   nssm install RedditMemeScraper "C:\path\to\venv\Scripts\python.exe" "C:\path\to\main.py"
   nssm start RedditMemeScraper
   ```

### Fedora/Ubuntu

1. **Run the Application**
   ```bash
   source venv/bin/activate
   python3 main.py
   ```

2. **Run as Systemd Service (Recommended)**
   ```bash
   sudo nano /etc/systemd/system/reddit-meme-scraper.service
   ```
   
   Add the following content:
   ```ini
   [Unit]
   Description=Reddit Meme Scraper Service
   After=network.target

   [Service]
   Type=simple
   User=<your-username>
   WorkingDirectory=/path/to/reddit_meme_scraper
   Environment=PATH=/path/to/reddit_meme_scraper/venv/bin
   ExecStart=/path/to/reddit_meme_scraper/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start the service:
   ```bash
   sudo systemctl enable reddit-meme-scraper
   sudo systemctl start reddit-meme-scraper
   ```

## Monitoring

### Webhook Notifications

The scraper supports webhook notifications for monitoring via Slack, Discord, or generic webhooks.

1. **Configure in `config.json`:**
   ```json
   {
     "monitoring": {
       "enabled": true,
       "webhook": {
         "enabled": true,
         "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
         "type": "slack"
       }
     }
   }
   ```

2. **Supported webhook types:**
   - `slack` - Slack incoming webhooks
   - `discord` - Discord webhooks
   - `generic` - Custom webhook format

3. **Notifications sent:**
   - Startup/shutdown events
   - Daily statistics reports
   - Error alerts
   - Successful meme batches

### E-ink Display Support (Raspberry Pi)

Perfect for your Raspberry Pi Zero W with e-ink display! The scraper can show real-time stats on supported e-ink displays.

1. **Setup e-ink display (Raspberry Pi only):**
   ```bash
   chmod +x setup_display.sh
   ./setup_display.sh
   ```

2. **Enable in `config.json`:**
   ```json
   {
     "display": {
       "enabled": true,
       "type": "epd2in13_V3"
     }
   }
   ```

3. **Supported displays:**
   - `epd2in13_V3` - 2.13" V3 display (most common for pwnagotchi)
   - `epd2in7` - 2.7" display

4. **Display shows:**
   - Total memes scraped/sent/failed
   - Last run time
   - System uptime
   - Current status (OK/ERROR)
   - Real-time updates every 5 minutes

**Note:** The application works perfectly without display support. Display libraries are optional and will be gracefully skipped if not available.

## Advanced Configuration

### Full `config.json` example:
```json
{
    "reddit": {
        "subreddits": ["memes", "dankmemes", "wholesomememes"],
        "sort_by": "hot",
        "limit": 10,
        "min_score": 100
    },
    "schedule": {
        "interval_hours": 1
    },
    "filters": {
        "image_only": true,
        "exclude_nsfw": false,
        "max_title_length": 200
    },
    "telegram": {
        "enabled": true
    },
    "monitoring": {
        "enabled": true,
        "webhook": {
            "enabled": true,
            "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "type": "slack"
        }
    },
    "display": {
        "enabled": true,
        "type": "epd2in13_V3"
    }
}
```

## Raspberry Pi Service Management

### Basic Service Commands
```bash
# Start the service
sudo systemctl start reddit-meme-scraper

# Stop the service
sudo systemctl stop reddit-meme-scraper

# Restart the service
sudo systemctl restart reddit-meme-scraper

# Check service status
sudo systemctl status reddit-meme-scraper

# Enable service to start on boot
sudo systemctl enable reddit-meme-scraper

# Disable service from starting on boot
sudo systemctl disable reddit-meme-scraper
```

### Logging Commands:
```bash
# View live logs (follow mode)
journalctl -u reddit-meme-scraper -f

# View last 100 lines of logs
journalctl -u reddit-meme-scraper -n 100

# View logs since last boot
journalctl -u reddit-meme-scraper -b

# View logs from a specific time
journalctl -u reddit-meme-scraper --since "2024-05-28 20:00:00"

# View error logs only
journalctl -u reddit-meme-scraper -p err
```

### Service Configuration
```bash
# Edit service configuration
sudo nano /etc/systemd/system/reddit-meme-scraper.service

# Reload systemd after configuration changes
sudo systemctl daemon-reload

# Verify service configuration
sudo systemctl cat reddit-meme-scraper
```

### Troubleshooting Commands
```bash
# Check if service is enabled
sudo systemctl is-enabled reddit-meme-scraper

# Check service dependencies
sudo systemctl list-dependencies reddit-meme-scraper

# Check service resource usage
sudo systemctl status reddit-meme-scraper -l

# View detailed service information
sudo systemctl show reddit-meme-scraper
```

## Monitoring (Traditional)

### Windows
- Check the logs in the project directory
- If running as a service, check Event Viewer

### Fedora/Ubuntu
- View service status:
  ```bash
  sudo systemctl status reddit-meme-scraper
  ```
- View logs:
  ```bash
  journalctl -u reddit-meme-scraper -f
  ```

## Troubleshooting

1. **Application Not Starting**
   - Check if Python is installed correctly
   - Verify all dependencies are installed
   - Check the `.env` file for correct credentials

2. **No Memes Being Sent**
   - Verify Reddit API credentials
   - Check Telegram bot token and chat ID
   - Ensure the bot is added to the target chat/channel

3. **Service Not Starting**
   - Check service status and logs
   - Verify file paths in service configuration
   - Ensure correct permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.