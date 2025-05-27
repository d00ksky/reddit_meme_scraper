import json
import logging
import os
from typing import Dict, Any

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('meme_scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

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