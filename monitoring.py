import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import time
import random

class MonitoringManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'scraped': 0,
            'sent': 0,
            'failed': 0,
            'last_run': None,
            'uptime_start': datetime.now(),
            'errors': [],
            'subreddit_stats': {},
            'last_error': None,
            'recent_memes': [],
            'best_meme_today': None
        }
        
        # Try to import e-ink display modules
        self.display = None
        self._init_display()
        
        # Start background monitoring thread
        if self.config.get('monitoring', {}).get('enabled', False):
            self._start_monitoring_thread()
    
    def _init_display(self):
        """Initialize e-ink display if available"""
        try:
            if not self.config.get('display', {}).get('enabled', False):
                return
            
            # Try to import Waveshare e-ink libraries (common for pwnagotchi)
            from PIL import Image, ImageDraw, ImageFont
            import sys
            
            # Check if we're on a Raspberry Pi
            if not os.path.exists('/proc/device-tree/model'):
                self.logger.info("Not on Raspberry Pi, skipping display init")
                return
            
            # Try different display types
            display_type = self.config.get('display', {}).get('type', 'epd2in13_V3')
            
            if display_type == 'epd2in13_V3':
                from waveshare_epd import epd2in13_V3
                self.display = FunEInkDisplay(epd2in13_V3.EPD(), 'epd2in13_V3', self.config)
            elif display_type == 'epd2in13_V4':
                from waveshare_epd import epd2in13_V4
                self.display = FunEInkDisplay(epd2in13_V4.EPD(), 'epd2in13_V4', self.config)
            elif display_type == 'epd2in7':
                from waveshare_epd import epd2in7
                self.display = FunEInkDisplay(epd2in7.EPD(), 'epd2in7', self.config)
            
            if self.display:
                self.display.init()
                self.logger.info(f"E-ink display ({display_type}) initialized")
                
        except ImportError:
            self.logger.info("E-ink display libraries not available, continuing without display")
        except Exception as e:
            self.logger.warning(f"Failed to initialize display: {e}")
    
    def _start_monitoring_thread(self):
        """Start background thread for periodic updates"""
        def monitor_loop():
            while True:
                try:
                    # Update display every 2 minutes instead of 30 seconds for stability
                    if self.display:
                        self._update_display()
                    
                    # Send daily reports
                    if self._should_send_daily_report():
                        self.send_daily_report()
                    
                    time.sleep(120)  # 2 minutes - much more stable for e-ink
                except Exception as e:
                    self.logger.error(f"Monitoring thread error: {e}")
                    time.sleep(300)  # 5 minutes on error
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        self.logger.info("Monitoring thread started (2-minute intervals for display stability)")
    
    def update_stats(self, event_type: str, **kwargs):
        """Update monitoring statistics"""
        if event_type == 'scraped':
            self.stats['scraped'] += kwargs.get('count', 1)
            subreddit = kwargs.get('subreddit')
            if subreddit:
                self.stats['subreddit_stats'][subreddit] = self.stats['subreddit_stats'].get(subreddit, 0) + kwargs.get('count', 1)
        
        elif event_type == 'sent':
            self.stats['sent'] += kwargs.get('count', 1)
            # Track recent memes
            meme = kwargs.get('meme')
            if meme:
                self.stats['recent_memes'].append({
                    'title': meme.get('title', '')[:30],
                    'subreddit': meme.get('subreddit', ''),
                    'score': meme.get('score', 0),
                    'url': meme.get('url', ''),  # Add URL for display
                    'sent_at': datetime.now()
                })
                # Keep only last 5 memes
                self.stats['recent_memes'] = self.stats['recent_memes'][-5:]
                
                # Track best meme of the day
                if not self.stats['best_meme_today'] or meme.get('score', 0) > self.stats['best_meme_today'].get('score', 0):
                    self.stats['best_meme_today'] = meme
        
        elif event_type == 'failed':
            self.stats['failed'] += kwargs.get('count', 1)
            error = kwargs.get('error')
            if error:
                self.stats['last_error'] = str(error)
                self.stats['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(error)
                })
                # Keep only last 10 errors
                self.stats['errors'] = self.stats['errors'][-10:]
        
        elif event_type == 'run_complete':
            self.stats['last_run'] = datetime.now()
        
        # Update display if available
        if self.display and event_type in ['sent', 'failed', 'run_complete']:
            self._update_display()
    
    def _update_display(self):
        """Update e-ink display with current stats"""
        if not self.display:
            return
        
        try:
            self.display.update_stats(self.stats)
        except Exception as e:
            self.logger.error(f"Display update failed: {e}")
    
    def send_webhook_notification(self, message: str, level: str = 'info'):
        """Send webhook notification"""
        webhook_config = self.config.get('monitoring', {}).get('webhook', {})
        if not webhook_config.get('enabled', False):
            return
        
        webhook_url = webhook_config.get('url')
        if not webhook_url:
            self.logger.warning("Webhook URL not configured")
            return
        
        try:
            # Format for different webhook types
            webhook_type = webhook_config.get('type', 'slack')
            
            if webhook_type == 'slack':
                payload = {
                    'text': f"🤖 Reddit Meme Scraper: {message}",
                    'username': 'Meme Bot'
                }
            elif webhook_type == 'discord':
                payload = {
                    'content': f"🤖 **Reddit Meme Scraper**: {message}"
                }
            else:  # Generic
                payload = {'message': message, 'level': level}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
    
    def send_daily_report(self):
        """Send daily statistics report"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        report = f"📊 Daily Report\n"
        report += f"Uptime: {uptime.days}d {uptime.seconds//3600}h\n"
        report += f"Scraped: {self.stats['scraped']} memes\n"
        report += f"Sent: {self.stats['sent']} memes\n"
        report += f"Failed: {self.stats['failed']} memes\n"
        
        if self.stats['subreddit_stats']:
            top_subreddit = max(self.stats['subreddit_stats'].items(), key=lambda x: x[1])
            report += f"Top subreddit: r/{top_subreddit[0]} ({top_subreddit[1]} memes)\n"
        
        if self.stats['best_meme_today']:
            report += f"Best meme: {self.stats['best_meme_today']['score']} upvotes\n"
        
        if self.stats['last_error']:
            report += f"Last error: {self.stats['last_error'][:100]}...\n"
        
        self.send_webhook_notification(report, 'info')
    
    def _should_send_daily_report(self):
        """Check if it's time to send daily report"""
        now = datetime.now()
        return now.hour == 9 and now.minute < 5  # Send at 9 AM daily


class FunEInkDisplay:
    def __init__(self, epd_driver, display_type, config=None):
        self.epd = epd_driver
        self.display_type = display_type
        self.config = config or {}
        self.width = epd_driver.height  # Note: rotated
        self.height = epd_driver.width
        self.animation_frame = 0
        self.current_meme_index = 0
        self.cached_memes = []  # Cache for downloaded meme images
        self.last_refresh_time = 0
        self.full_refresh_counter = 0
        self.previous_image = None  # Store previous image to compare
        
        # Check if meme images should be displayed
        self.show_meme_images = self.config.get('display', {}).get('show_meme_images', True)
        
        # Display stability settings from config
        display_config = self.config.get('display', {})
        self.min_refresh_interval = display_config.get('refresh_interval_minutes', 2) * 60  # Convert to seconds
        self.mode_change_interval = display_config.get('mode_change_minutes', 5) * 60  # Convert to seconds
        self.full_refresh_every = 6  # Full refresh every 6 updates (reduces ghosting)
        self.enable_partial_refresh = display_config.get('enable_partial_refresh', True)
        
        # Import PIL here since it's only needed if display is available
        from PIL import Image, ImageDraw, ImageFont
        self.Image = Image
        self.ImageDraw = ImageDraw
        self.ImageFont = ImageFont
        
        # Fun ASCII art and emojis
        self.meme_faces = ["(͡° ͜ʖ ͡°)", "ಠ_ಠ", "¯\\_(ツ)_/¯", "( ͡° ͡°)", "◉_◉", "ಥ_ಥ"]
        self.success_emojis = ["🎉", "🚀", "✨", "🔥", "💯", "🎊"]
        self.error_faces = ["(╯°□°）╯", "¯\\_(ツ)_/¯", "(┛ಠ_ಠ)┛", "ಠ╭╮ಠ"]
        
        # Try to load fonts
        try:
            self.font_tiny = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
            self.font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            self.font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            self.font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        except:
            # Fallback to default font
            self.font_tiny = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def init(self):
        """Initialize the display"""
        self.epd.init()
        
        # Clear display once at startup
        self.epd.Clear(0xFF)
        
        # Show startup message (only once)
        self._show_startup_animation()
        
        # Initialize partial refresh if supported
        try:
            if hasattr(self.epd, 'init_partial'):
                self.epd.init_partial()
                print("Partial refresh mode enabled")
        except:
            print("Partial refresh not supported, using full refresh")
            self.enable_partial_refresh = False
    
    def _show_startup_animation(self):
        """Show animated startup sequence"""
        frames = [
            "MEME SCRAPER",
            "INITIALIZING...",
            "LOADING DANK MEMES",
            "READY TO SERVE! (͡° ͜ʖ ͡°)"
        ]
        
        for i, text in enumerate(frames):
            image = self.Image.new('1', (self.width, self.height), 255)
            draw = self.ImageDraw.Draw(image)
            
            # Fun border
            self._draw_border(draw)
            
            # Centered text
            text_bbox = draw.textbbox((0, 0), text, font=self.font_medium)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            draw.text((x, y), text, font=self.font_medium, fill=0)
            
            # Add loading dots
            dots = "." * ((i % 3) + 1)
            draw.text((x, y + 25), dots, font=self.font_small, fill=0)
            
            self.epd.display(self.epd.getbuffer(image))
            time.sleep(1)
    
    def update_stats(self, stats):
        """Update display with fun, dynamic statistics"""
        # Only change display mode occasionally to reduce flicker
        import time
        current_time = time.time()
        
        # Change display mode based on configuration (default: every 5 minutes)
        if current_time - self.last_refresh_time >= self.mode_change_interval:
            # Determine number of display modes based on configuration
            max_modes = 5 if self.show_meme_images else 4
            self.animation_frame = (self.animation_frame + 1) % max_modes
        
        image = self.Image.new('1', (self.width, self.height), 255)
        draw = self.ImageDraw.Draw(image)
        
        if self.animation_frame == 0:
            self._draw_main_stats(draw, stats)
        elif self.animation_frame == 1:
            self._draw_recent_memes(draw, stats)
        elif self.animation_frame == 2:
            self._draw_subreddit_stats(draw, stats)
        elif self.animation_frame == 3:
            self._draw_fun_status(draw, stats)
        elif self.animation_frame == 4 and self.show_meme_images:
            self._draw_meme_display_stable(draw, stats)
            return  # _draw_meme_display_stable handles its own refresh
        
        # Use smart refresh instead of direct display
        self._smart_refresh(image)
    
    def _draw_border(self, draw, style='fancy'):
        """Draw decorative borders"""
        if style == 'fancy':
            # Corner decorations
            draw.text((2, 2), "╔", font=self.font_small, fill=0)
            draw.text((self.width-10, 2), "╗", font=self.font_small, fill=0)
            draw.text((2, self.height-15), "╚", font=self.font_small, fill=0)
            draw.text((self.width-10, self.height-15), "╝", font=self.font_small, fill=0)
            
            # Top and bottom lines
            for i in range(15, self.width-15, 10):
                draw.text((i, 2), "═", font=self.font_small, fill=0)
                draw.text((i, self.height-15), "═", font=self.font_small, fill=0)
        else:
            # Simple rectangle
            draw.rectangle([1, 1, self.width-2, self.height-2], outline=0, width=1)
    
    def _draw_main_stats(self, draw, stats):
        """Main statistics screen with fun elements"""
        self._draw_border(draw)
        
        # Title with emoji
        title = f"🎭 MEME STATS 🎭"
        title_bbox = draw.textbbox((0, 0), title, font=self.font_medium)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((self.width - title_width) // 2, 8), title, font=self.font_medium, fill=0)
        
        # Stats with fun formatting
        y = 35
        draw.text((10, y), f"📥 Scraped: {stats['scraped']}", font=self.font_small, fill=0)
        y += 18
        draw.text((10, y), f"📤 Sent: {stats['sent']}", font=self.font_small, fill=0)
        y += 18
        draw.text((10, y), f"❌ Failed: {stats['failed']}", font=self.font_small, fill=0)
        
        # Success rate
        if stats['scraped'] > 0:
            success_rate = int((stats['sent'] / stats['scraped']) * 100)
            y += 25
            emoji = "🔥" if success_rate > 80 else "👍" if success_rate > 60 else "😐"
            draw.text((10, y), f"{emoji} Rate: {success_rate}%", font=self.font_small, fill=0)
        
        # Uptime
        uptime = datetime.now() - stats['uptime_start']
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h"
        draw.text((10, self.height - 35), f"⏰ Up: {uptime_str}", font=self.font_tiny, fill=0)
        
        # Last run with face
        if stats['last_run']:
            last_run_str = stats['last_run'].strftime("%H:%M")
            face = random.choice(self.meme_faces)
            draw.text((10, self.height - 20), f"Last: {last_run_str} {face}", font=self.font_tiny, fill=0)
    
    def _draw_recent_memes(self, draw, stats):
        """Show recent memes with titles"""
        self._draw_border(draw)
        
        draw.text((10, 8), "🔥 RECENT MEMES 🔥", font=self.font_medium, fill=0)
        
        if stats['recent_memes']:
            y = 30
            for i, meme in enumerate(stats['recent_memes'][-3:]):  # Show last 3
                # Truncate title
                title = meme['title'][:20] + "..." if len(meme['title']) > 20 else meme['title']
                draw.text((5, y), f"r/{meme['subreddit']}", font=self.font_tiny, fill=0)
                y += 12
                draw.text((5, y), title, font=self.font_small, fill=0)
                y += 12
                draw.text((5, y), f"⬆ {meme['score']}", font=self.font_tiny, fill=0)
                y += 20
        else:
            draw.text((10, 50), "No memes yet (╯°□°）╯", font=self.font_small, fill=0)
    
    def _draw_subreddit_stats(self, draw, stats):
        """Show subreddit leaderboard"""
        self._draw_border(draw)
        
        draw.text((10, 8), "🏆 TOP SUBREDDITS", font=self.font_medium, fill=0)
        
        if stats['subreddit_stats']:
            # Sort by count
            sorted_subs = sorted(stats['subreddit_stats'].items(), key=lambda x: x[1], reverse=True)
            
            y = 30
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (subreddit, count) in enumerate(sorted_subs[:5]):
                medal = medals[i] if i < len(medals) else "•"
                text = f"{medal} r/{subreddit}: {count}"
                draw.text((5, y), text, font=self.font_small, fill=0)
                y += 15
        else:
            draw.text((10, 50), "No stats yet ¯\\_(ツ)_/¯", font=self.font_small, fill=0)
    
    def _draw_fun_status(self, draw, stats):
        """Fun status screen with animations"""
        self._draw_border(draw)
        
        # Determine status
        if stats['last_error']:
            status = "ERROR"
            face = random.choice(self.error_faces)
            emoji = "💥"
        elif stats['sent'] > 0:
            status = "SENDING MEMES"
            face = random.choice(self.meme_faces)
            emoji = random.choice(self.success_emojis)
        else:
            status = "WAITING..."
            face = "(･_･)"
            emoji = "😴"
        
        # Big status
        draw.text((10, 15), f"{emoji} {status}", font=self.font_large, fill=0)
        
        # Fun face
        face_bbox = draw.textbbox((0, 0), face, font=self.font_medium)
        face_width = face_bbox[2] - face_bbox[0]
        draw.text(((self.width - face_width) // 2, 45), face, font=self.font_medium, fill=0)
        
        # Meme counter
        if stats['sent'] > 0:
            counter_text = f"Memes delivered: {stats['sent']}"
            draw.text((10, 80), counter_text, font=self.font_small, fill=0)
            
            # Celebration for milestones
            if stats['sent'] % 10 == 0 and stats['sent'] > 0:
                draw.text((10, 95), "🎉 MILESTONE! 🎉", font=self.font_small, fill=0)
        
        # Current time
        now = datetime.now().strftime("%H:%M:%S")
        draw.text((10, self.height - 15), now, font=self.font_tiny, fill=0)
    
    def _draw_meme_display_stable(self, draw, stats):
        """Display actual meme images with stable refresh"""
        if not stats.get('recent_memes'):
            # No memes to display
            image = self.Image.new('1', (self.width, self.height), 255)
            draw = self.ImageDraw.Draw(image)
            self._draw_border(draw)
            draw.text((10, 8), "🎭 MEME DISPLAY 🎭", font=self.font_medium, fill=0)
            
            face = random.choice(self.meme_faces)
            draw.text((10, 50), f"No memes cached yet {face}", font=self.font_small, fill=0)
            draw.text((10, 70), "Check back soon!", font=self.font_small, fill=0)
            self._smart_refresh(image)
            return
        
        # Get current meme
        recent_memes = stats['recent_memes']
        if self.current_meme_index >= len(recent_memes):
            self.current_meme_index = 0
        
        current_meme = recent_memes[self.current_meme_index]
        
        # Try to download and display the meme
        if current_meme.get('url'):
            processed_img, meme_data = self._download_meme_image(current_meme)
            
            if processed_img:
                # Clear display
                image = self.Image.new('1', (self.width, self.height), 255)
                draw = self.ImageDraw.Draw(image)
                
                # Draw border
                draw.rectangle([0, 0, self.width-1, self.height-1], outline=0, width=1)
                
                # Calculate position to center the image
                img_x = (self.width - processed_img.width) // 2
                img_y = 25  # Leave space for title
                
                # Paste the meme image
                image.paste(processed_img, (img_x, img_y))
                
                # Add title at top
                title = current_meme['title'][:30] + "..." if len(current_meme['title']) > 30 else current_meme['title']
                title_bbox = draw.textbbox((0, 0), title, font=self.font_small)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 5), title, font=self.font_small, fill=0)
                
                # Add info at bottom
                info = f"r/{current_meme['subreddit']} • ⬆{current_meme['score']}"
                draw.text((5, self.height - 15), info, font=self.font_tiny, fill=0)
                
                # Use smart refresh
                if self._smart_refresh(image):
                    # Move to next meme only if refresh was successful
                    self.current_meme_index = (self.current_meme_index + 1) % len(recent_memes)
                return
        
        # Fallback if image download failed
        image = self.Image.new('1', (self.width, self.height), 255)
        draw = self.ImageDraw.Draw(image)
        self._draw_border(draw)
        draw.text((10, 8), "🎭 MEME DISPLAY 🎭", font=self.font_medium, fill=0)
        
        title = current_meme['title'][:25] + "..." if len(current_meme['title']) > 25 else current_meme['title']
        draw.text((10, 30), title, font=self.font_small, fill=0)
        draw.text((10, 50), f"r/{current_meme['subreddit']}", font=self.font_small, fill=0)
        draw.text((10, 70), f"⬆ {current_meme['score']} upvotes", font=self.font_small, fill=0)
        
        # Add a meme face
        face = random.choice(self.meme_faces)
        face_bbox = draw.textbbox((0, 0), face, font=self.font_large)
        face_width = face_bbox[2] - face_bbox[0]
        draw.text(((self.width - face_width) // 2, 90), face, font=self.font_large, fill=0)
        
        draw.text((10, self.height - 15), "Image download failed :(", font=self.font_tiny, fill=0)
        self._smart_refresh(image)
    
    def _download_meme_image(self, meme_data):
        """Download and process a meme image for display"""
        try:
            import requests
            from io import BytesIO
            
            # Download the image
            response = requests.get(meme_data['url'], timeout=10, headers={
                'User-Agent': 'RedditMemeScraper/1.0'
            })
            response.raise_for_status()
            
            # Open and process the image
            img = self.Image.open(BytesIO(response.content))
            
            # Convert to grayscale and resize to fit display
            img = img.convert('L')  # Grayscale
            
            # Calculate scaling to fit display while maintaining aspect ratio
            img_ratio = img.width / img.height
            display_ratio = self.width / self.height
            
            if img_ratio > display_ratio:
                # Image is wider, scale by width
                new_width = self.width - 20  # Leave margin
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller, scale by height
                new_height = self.height - 60  # Leave space for title/info
                new_width = int(new_height * img_ratio)
            
            img = img.resize((new_width, new_height), self.Image.Resampling.LANCZOS)
            
            # Convert to 1-bit for e-ink display
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            
            return img, meme_data
            
        except Exception as e:
            print(f"Failed to download meme image: {e}")
            return None, None
    
    def _smart_refresh(self, image):
        """Smart refresh that uses partial refresh when possible and rate limits updates"""
        import time
        
        current_time = time.time()
        
        # Rate limiting: don't update too frequently
        if current_time - self.last_refresh_time < self.min_refresh_interval:
            return False
        
        # Check if image actually changed (avoid unnecessary refreshes)
        if self.previous_image:
            # Simple comparison - convert both to bytes and compare
            try:
                if image.tobytes() == self.previous_image.tobytes():
                    return False  # No change, skip refresh
            except:
                pass  # If comparison fails, proceed with refresh
        
        # Determine refresh type
        use_partial = (self.enable_partial_refresh and 
                      hasattr(self.epd, 'displayPartial') and
                      self.full_refresh_counter < self.full_refresh_every)
        
        try:
            if use_partial:
                # Use partial refresh (faster, less flicker)
                if hasattr(self.epd, 'displayPartial'):
                    self.epd.displayPartial(self.epd.getbuffer(image))
                else:
                    self.epd.display(self.epd.getbuffer(image))
                self.full_refresh_counter += 1
            else:
                # Use full refresh (clears ghosting)
                self.epd.display(self.epd.getbuffer(image))
                self.full_refresh_counter = 0
                
            self.last_refresh_time = current_time
            self.previous_image = image.copy()
            return True
            
        except Exception as e:
            print(f"Display refresh failed: {e}")
            return False 