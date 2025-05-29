import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import time

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
            'last_error': None
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
                self.display = EInkDisplay(epd2in13_V3.EPD(), 'epd2in13_V3')
            elif display_type == 'epd2in7':
                from waveshare_epd import epd2in7
                self.display = EInkDisplay(epd2in7.EPD(), 'epd2in7')
            
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
                    # Update display every 5 minutes
                    if self.display:
                        self._update_display()
                    
                    # Send daily reports
                    if self._should_send_daily_report():
                        self.send_daily_report()
                    
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    self.logger.error(f"Monitoring thread error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        self.logger.info("Monitoring thread started")
    
    def update_stats(self, event_type: str, **kwargs):
        """Update monitoring statistics"""
        if event_type == 'scraped':
            self.stats['scraped'] += kwargs.get('count', 1)
            subreddit = kwargs.get('subreddit')
            if subreddit:
                self.stats['subreddit_stats'][subreddit] = self.stats['subreddit_stats'].get(subreddit, 0) + kwargs.get('count', 1)
        
        elif event_type == 'sent':
            self.stats['sent'] += kwargs.get('count', 1)
        
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
        
        if self.stats['last_error']:
            report += f"Last error: {self.stats['last_error'][:100]}...\n"
        
        self.send_webhook_notification(report, 'info')
    
    def _should_send_daily_report(self):
        """Check if it's time to send daily report"""
        now = datetime.now()
        return now.hour == 9 and now.minute < 5  # Send at 9 AM daily


class EInkDisplay:
    def __init__(self, epd_driver, display_type):
        self.epd = epd_driver
        self.display_type = display_type
        self.width = epd_driver.height  # Note: rotated
        self.height = epd_driver.width
        
        # Import PIL here since it's only needed if display is available
        from PIL import Image, ImageDraw, ImageFont
        self.Image = Image
        self.ImageDraw = ImageDraw
        self.ImageFont = ImageFont
        
        # Try to load a font
        try:
            self.font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            self.font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            self.font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except:
            # Fallback to default font
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def init(self):
        """Initialize the display"""
        self.epd.init()
        self.epd.Clear(0xFF)
        
        # Show startup message
        self._show_startup_screen()
    
    def _show_startup_screen(self):
        """Show initial startup message"""
        image = self.Image.new('1', (self.width, self.height), 255)
        draw = self.ImageDraw.Draw(image)
        
        draw.text((10, 10), "Reddit Meme Scraper", font=self.font_large, fill=0)
        draw.text((10, 40), "Starting up...", font=self.font_medium, fill=0)
        draw.text((10, 70), f"Display: {self.display_type}", font=self.font_small, fill=0)
        
        self.epd.display(self.epd.getbuffer(image))
    
    def update_stats(self, stats):
        """Update display with current statistics"""
        image = self.Image.new('1', (self.width, self.height), 255)
        draw = self.ImageDraw.Draw(image)
        
        # Header
        draw.text((5, 5), "Meme Scraper Status", font=self.font_medium, fill=0)
        
        # Stats
        y = 30
        draw.text((5, y), f"Scraped: {stats['scraped']}", font=self.font_small, fill=0)
        y += 20
        draw.text((5, y), f"Sent: {stats['sent']}", font=self.font_small, fill=0)
        y += 20
        draw.text((5, y), f"Failed: {stats['failed']}", font=self.font_small, fill=0)
        
        # Last run time
        if stats['last_run']:
            y += 25
            last_run_str = stats['last_run'].strftime("%H:%M")
            draw.text((5, y), f"Last run: {last_run_str}", font=self.font_small, fill=0)
        
        # Uptime
        uptime = datetime.now() - stats['uptime_start']
        y += 20
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h"
        draw.text((5, y), f"Uptime: {uptime_str}", font=self.font_small, fill=0)
        
        # Status indicator
        if stats['last_error']:
            draw.text((5, self.height - 25), "Status: ERROR", font=self.font_small, fill=0)
        else:
            draw.text((5, self.height - 25), "Status: OK", font=self.font_small, fill=0)
        
        # Update timestamp
        now = datetime.now().strftime("%H:%M:%S")
        draw.text((5, self.height - 10), f"Updated: {now}", font=self.font_small, fill=0)
        
        self.epd.display(self.epd.getbuffer(image)) 