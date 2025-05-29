import os
import logging
import asyncio
from typing import List, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application
import httpx

class TelegramSender:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Telegram bot
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in environment variables")
        
        # Create bot with custom HTTP client settings
        self.bot = None
        self._create_bot()
        self.logger.info("Telegram sender initialized")
    
    def _create_bot(self):
        """Create a new bot instance with proper connection pool settings"""
        # Custom HTTP client with proper connection pool settings
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            follow_redirects=True
        )
        
        self.bot = Bot(
            token=self.bot_token,
            get_updates_http_version='1.1',
            http_version='1.1'
        )
        # Set the custom HTTP client
        self.bot._httpx_client = http_client
    
    def send_memes(self, memes: List[Dict[str, Any]]):
        """Send memes via Telegram"""
        if not self.config.get('telegram', {}).get('enabled', True):
            self.logger.info("Telegram sending is disabled")
            return
        
        if not memes:
            self.logger.info("No memes to send")
            return
        
        # Refresh bot connection to prevent pool timeouts
        self._refresh_connection()
        
        # Run async function in sync context
        asyncio.run(self._send_memes_async(memes))
    
    def _refresh_connection(self):
        """Refresh the bot connection to prevent timeouts"""
        try:
            if self.bot and hasattr(self.bot, '_httpx_client'):
                # Close existing client
                asyncio.run(self.bot._httpx_client.aclose())
            
            # Create new bot instance
            self._create_bot()
            self.logger.debug("Refreshed Telegram bot connection")
        except Exception as e:
            self.logger.warning(f"Error refreshing connection: {e}")
            # Fallback to creating new bot
            self._create_bot()
    
    async def _send_memes_async(self, memes: List[Dict[str, Any]]):
        """Async function to send memes"""
        try:
            for meme in memes:
                try:
                    await self._send_single_meme(meme)
                    # Small delay between messages to avoid rate limiting
                    await asyncio.sleep(1)
                except Exception as e:
                    self.logger.error(f"Failed to send meme {meme['id']}: {e}")
        finally:
            # Clean up connections after sending
            if self.bot and hasattr(self.bot, '_httpx_client'):
                try:
                    await self.bot._httpx_client.aclose()
                except Exception as e:
                    self.logger.debug(f"Error closing HTTP client: {e}")
    
    async def _send_single_meme(self, meme: Dict[str, Any]):
        """Send a single meme"""
        try:
            # Prepare caption
            caption = self._format_caption(meme)
            
            # Send photo with caption
            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=meme['image_url'],
                caption=caption,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Sent meme: {meme['title'][:50]}...")
            
        except TelegramError as e:
            if "photo_invalid_dimensions" in str(e) or "failed to get HTTP URL content" in str(e):
                # Try sending as document if photo fails
                await self._send_as_document(meme)
            else:
                raise e
    
    async def _send_as_document(self, meme: Dict[str, Any]):
        """Send meme as document if photo sending fails"""
        try:
            caption = self._format_caption(meme)
            
            await self.bot.send_document(
                chat_id=self.chat_id,
                document=meme['image_url'],
                caption=caption,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Sent meme as document: {meme['title'][:50]}...")
            
        except TelegramError as e:
            # If document also fails, send just the text with URL
            await self._send_text_fallback(meme)
    
    async def _send_text_fallback(self, meme: Dict[str, Any]):
        """Fallback to sending just text with URL"""
        try:
            message = f"*{meme['title']}*\n\n"
            message += f"r/{meme['subreddit']} • {meme['score']} upvotes\n"
            message += f"[View Image]({meme['image_url']})\n"
            message += f"[Reddit Post]({meme['permalink']})"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            
            self.logger.info(f"Sent meme as text: {meme['title'][:50]}...")
            
        except Exception as e:
            self.logger.error(f"All sending methods failed for meme {meme['id']}: {e}")
    
    def _format_caption(self, meme: Dict[str, Any]) -> str:
        """Format caption for the meme"""
        caption = f"*{meme['title']}*\n\n"
        caption += f"📍 r/{meme['subreddit']}\n"
        caption += f"⬆️ {meme['score']} upvotes\n"
        caption += f"👤 u/{meme['author']}\n\n"
        caption += f"[View on Reddit]({meme['permalink']})"
        
        # Telegram caption limit is 1024 characters
        if len(caption) > 1024:
            caption = caption[:1020] + "..."
        
        return caption 