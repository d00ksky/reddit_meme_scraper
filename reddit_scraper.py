import os
import praw
import logging
from typing import List, Dict, Any
from utils import is_image_url, load_sent_posts, save_sent_posts

class RedditScraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sent_posts = load_sent_posts()
        
        # Initialize Reddit instance
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        self.logger.info("Reddit scraper initialized")
    
    def scrape_memes(self) -> List[Dict[str, Any]]:
        """Scrape memes from configured subreddits"""
        memes = []
        reddit_config = self.config.get('reddit', {})
        filters = self.config.get('filters', {})
        
        subreddits = reddit_config.get('subreddits', ['memes'])
        sort_by = reddit_config.get('sort_by', 'hot')
        limit = reddit_config.get('limit', 10)
        min_score = reddit_config.get('min_score', 100)
        
        for subreddit_name in subreddits:
            try:
                self.logger.info(f"Scraping r/{subreddit_name}")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get posts based on sorting method
                if sort_by == 'hot':
                    posts = subreddit.hot(limit=limit)
                elif sort_by == 'new':
                    posts = subreddit.new(limit=limit)
                elif sort_by == 'top':
                    posts = subreddit.top('day', limit=limit)
                else:
                    posts = subreddit.hot(limit=limit)
                
                for post in posts:
                    # Skip if already sent
                    if post.id in self.sent_posts:
                        continue
                    
                    # Apply filters
                    if not self._passes_filters(post, filters, min_score):
                        continue
                    
                    # Extract meme data
                    meme_data = self._extract_meme_data(post, subreddit_name)
                    if meme_data:
                        memes.append(meme_data)
                        self.sent_posts.add(post.id)
                        
            except Exception as e:
                self.logger.error(f"Error scraping r/{subreddit_name}: {e}")
        
        # Save updated sent posts
        save_sent_posts(self.sent_posts)
        
        self.logger.info(f"Found {len(memes)} new memes")
        return memes
    
    def _passes_filters(self, post, filters: Dict[str, Any], min_score: int) -> bool:
        """Check if post passes all filters"""
        
        # Score filter
        if post.score < min_score:
            return False
        
        # NSFW filter
        if filters.get('exclude_nsfw', True) and post.over_18:
            return False
        
        # Title length filter
        max_title_length = filters.get('max_title_length', 200)
        if len(post.title) > max_title_length:
            return False
        
        # Image only filter
        if filters.get('image_only', True):
            if not (is_image_url(post.url) or hasattr(post, 'post_hint') and post.post_hint == 'image'):
                return False
        
        return True
    
    def _extract_meme_data(self, post, subreddit_name: str) -> Dict[str, Any]:
        """Extract relevant data from a Reddit post"""
        try:
            # Handle different types of image posts
            image_url = None
            
            if is_image_url(post.url):
                image_url = post.url
            elif hasattr(post, 'preview') and 'images' in post.preview:
                # Get the highest resolution image
                images = post.preview['images'][0]['resolutions']
                if images:
                    image_url = images[-1]['url'].replace('&amp;', '&')
                else:
                    image_url = post.preview['images'][0]['source']['url'].replace('&amp;', '&')
            elif post.url.startswith('https://i.redd.it/'):
                image_url = post.url
            
            if not image_url:
                return None
            
            return {
                'id': post.id,
                'title': post.title,
                'url': post.url,
                'image_url': image_url,
                'score': post.score,
                'subreddit': subreddit_name,
                'author': str(post.author) if post.author else 'Unknown',
                'created_utc': post.created_utc,
                'permalink': f"https://reddit.com{post.permalink}"
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting data from post {post.id}: {e}")
            return None 