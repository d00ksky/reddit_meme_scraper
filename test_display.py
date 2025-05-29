#!/usr/bin/env python3
"""
E-ink Display Test and Reset Script
Designed to refresh old images, test functionality, and remove ghosting
"""

import time
import sys
import os
from PIL import Image, ImageDraw, ImageFont

def detect_display_model():
    """Try to detect which display model is connected"""
    models_to_try = [
        ('epd2in13_V3', 'Most common pwnagotchi display'),
        ('epd2in13_V2', 'Older 2.13" version'), 
        ('epd2in13_V4', 'Newer 2.13" version'),
        ('epd2in13', 'Original 2.13" version'),
        ('epd2in7', '2.7" display')
    ]
    
    print("🔍 Detecting display model...")
    
    for model, description in models_to_try:
        try:
            print(f"   Trying {model} ({description})...")
            module = __import__(f'waveshare_epd.{model}', fromlist=[model])
            epd_class = getattr(module, 'EPD')
            epd = epd_class()
            print(f"✅ Found: {model}")
            return epd, model
        except ImportError as e:
            print(f"   ❌ Module {model} not available: {e}")
        except Exception as e:
            print(f"   ❌ Failed to initialize {model}: {e}")
    
    print("❌ No compatible display found!")
    return None, None

def aggressive_clean(epd, model):
    """Perform aggressive cleaning to remove ghosting/burn-in"""
    print("\n🧹 Starting aggressive display cleaning...")
    
    try:
        # Initialize display
        print("   Initializing display...")
        epd.init()
        
        width = epd.height  # Note: dimensions are swapped
        height = epd.width
        
        print(f"   Display size: {width}x{height}")
        
        # Step 1: Multiple full clears
        print("   Step 1: Full display clearing (5 cycles)...")
        for i in range(5):
            print(f"      Clear cycle {i+1}/5")
            epd.Clear(0xFF)  # White
            time.sleep(2)
            epd.Clear(0x00)  # Black  
            time.sleep(2)
        
        # Step 2: Rapid black/white flashing
        print("   Step 2: Rapid refresh cycles (10 cycles)...")
        black_img = Image.new('1', (width, height), 0)   # Black
        white_img = Image.new('1', (width, height), 255) # White
        
        for i in range(10):
            print(f"      Flash cycle {i+1}/10")
            epd.display(epd.getbuffer(black_img))
            time.sleep(0.5)
            epd.display(epd.getbuffer(white_img))
            time.sleep(0.5)
        
        # Step 3: Gradient patterns to exercise all pixels
        print("   Step 3: Gradient pattern refresh...")
        for pattern in ['vertical', 'horizontal', 'checkerboard']:
            print(f"      Pattern: {pattern}")
            img = create_test_pattern(width, height, pattern)
            epd.display(epd.getbuffer(img))
            time.sleep(2)
            
        # Step 4: Final clear
        print("   Step 4: Final clear...")
        epd.Clear(0xFF)
        time.sleep(2)
        
        print("✅ Aggressive cleaning completed!")
        return width, height
        
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")
        return None, None

def create_test_pattern(width, height, pattern_type):
    """Create various test patterns"""
    img = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(img)
    
    if pattern_type == 'vertical':
        # Vertical stripes
        for x in range(0, width, 20):
            draw.rectangle([x, 0, x+10, height], fill=0)
    
    elif pattern_type == 'horizontal':
        # Horizontal stripes  
        for y in range(0, height, 20):
            draw.rectangle([0, y, width, y+10], fill=0)
    
    elif pattern_type == 'checkerboard':
        # Checkerboard pattern
        square_size = 20
        for x in range(0, width, square_size):
            for y in range(0, height, square_size):
                if ((x // square_size) + (y // square_size)) % 2:
                    draw.rectangle([x, y, x+square_size, y+square_size], fill=0)
    
    return img

def create_test_display(width, height, model):
    """Create a comprehensive test display"""
    img = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16) 
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default() 
        font_small = ImageFont.load_default()
    
    # Border
    draw.rectangle([2, 2, width-3, height-3], outline=0, width=2)
    
    # Title
    title = "E-INK TEST SUCCESS!"
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 10), title, font=font_large, fill=0)
    
    # Display model
    model_text = f"Model: {model}"
    draw.text((10, 40), model_text, font=font_medium, fill=0)
    
    # Test patterns
    y = 65
    draw.text((10, y), "Test Patterns:", font=font_medium, fill=0)
    
    # Small test patterns
    y += 25
    
    # Dots
    for i in range(5):
        draw.ellipse([10 + i*15, y, 20 + i*15, y+10], fill=0)
    
    # Lines
    y += 20
    for i in range(5):
        thickness = i + 1
        draw.rectangle([10, y + i*3, 80, y + i*3 + thickness], fill=0)
    
    # Text quality test
    y += 25
    draw.text((10, y), "Text Quality: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", font=font_small, fill=0)
    
    # Meme face for fun
    y += 20
    meme_face = "(͡° ͜ʖ ͡°) Display Working!"
    face_bbox = draw.textbbox((0, 0), meme_face, font=font_medium)
    face_width = face_bbox[2] - face_bbox[0]
    draw.text(((width - face_width) // 2, y), meme_face, font=font_medium, fill=0)
    
    # Timestamp
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, height - 25), f"Test completed: {current_time}", font=font_small, fill=0)
    
    return img

def run_display_test():
    """Main function to run the complete display test"""
    print("🎭 E-ink Display Test & Reset Script")
    print("=" * 50)
    
    # Check if running on Raspberry Pi
    if not os.path.exists('/proc/device-tree/model'):
        print("⚠️  Warning: Not running on Raspberry Pi")
        print("   This script is designed for Raspberry Pi with e-ink displays")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Try to import waveshare library
    try:
        import waveshare_epd
        print("✅ Waveshare EPD library found")
    except ImportError:
        print("❌ Waveshare EPD library not found!")
        print("   Run: sudo python3 setup.py install")
        print("   From: /tmp/e-Paper-master/RaspberryPi_JetsonNano/python/")
        sys.exit(1)
    
    # Detect display
    epd, model = detect_display_model()
    if not epd:
        print("❌ No display detected. Check connections!")
        sys.exit(1)
    
    try:
        # Aggressive cleaning to remove ghosting
        width, height = aggressive_clean(epd, model)
        if not width:
            print("❌ Cleaning failed!")
            sys.exit(1)
        
        # Create and display test image
        print("\n🎨 Creating test display...")
        test_img = create_test_display(width, height, model)
        
        print("   Displaying test image...")
        epd.display(epd.getbuffer(test_img))
        
        print("\n✅ Test completed successfully!")
        print(f"   Display model: {model}")
        print(f"   Resolution: {width}x{height}")
        print("   Check your display - you should see a test pattern with text")
        
        # Ask if user wants to clear the display
        print("\n🧹 Display test is complete.")
        response = input("   Clear display and sleep? (Y/n): ")
        if response.lower() != 'n':
            print("   Clearing display...")
            epd.Clear(0xFF)
            print("   Putting display to sleep...")
            epd.sleep()
            print("   Display cleared and sleeping.")
        else:
            print("   Leaving test image on display.")
            epd.sleep()
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        try:
            epd.sleep()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_display_test() 