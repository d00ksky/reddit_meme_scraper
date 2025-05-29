import json
import logging
import os
from typing import Dict, Any

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    # Determine log file location
    if os.getenv('INVOCATION_ID'):  # Running under systemd
        log_file = '/var/log/reddit-meme-scraper.log'
        # Try to create the log file with proper permissions
        try:
            with open(log_file, 'a') as f:
                pass
        except PermissionError:
            # Fall back to user's home directory
            log_file = os.path.expanduser('~/reddit_meme_scraper.log')
    else:
        # Running manually, use current directory
        log_file = 'meme_scraper.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to: {log_file}")
    return logger

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("config.json not found. Please create it based on the example.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in config.json")

def is_image_url(url: str) -> bool:
    """Check if URL points to an image"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    return any(url.lower().endswith(ext) for ext in image_extensions)

def load_sent_posts() -> set:
    """Load previously sent post IDs"""
    try:
        with open('sent_posts.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_sent_posts(sent_posts: set):
    """Save sent post IDs to prevent duplicates"""
    with open('sent_posts.json', 'w') as f:
        json.dump(list(sent_posts), f) 