# RGB Strip Module for Freenove 8-RGB-LED Module
# Controls 8 addressable RGB LEDs for Smart Home status

import sys
sys.path.append('lib')
sys.path.append('..')  # To access config
from neopixel import NeoPixel
from machine import Pin
import time

# Import configuration
try:
    from config import SMART_HOME_PINS, RGB_CONFIG
except ImportError:
    # Fallback if config not available
    SMART_HOME_PINS = {'RGB_STRIP': 2}
    RGB_CONFIG = {
        'NUM_LEDS': 8,
        'DEFAULT_BRIGHTNESS': 128,
        'ANIMATION_SPEED': 50,
        'STATUS_COLORS': {
            'ready': (0, 255, 0),
            'error': (255, 0, 0),
            'warning': (255, 128, 0),
            'info': (0, 0, 255),
            'off': (0, 0, 0)
        }
    }

class RGBStrip:
    def __init__(self, pin=None, num_leds=None):
        """Initialize 8-RGB-LED strip on specified pin"""
        # Use config values if not specified
        if pin is None:
            pin = SMART_HOME_PINS['RGB_STRIP']
        if num_leds is None:
            num_leds = RGB_CONFIG['NUM_LEDS']
        
        self.pin = Pin(pin, Pin.OUT)
        self.num_leds = num_leds
        self.strip = NeoPixel(self.pin, num_leds)
        self.current_status = "initializing"
        
        # Configuration from config.py
        self.default_brightness = RGB_CONFIG['DEFAULT_BRIGHTNESS']
        self.animation_speed = RGB_CONFIG['ANIMATION_SPEED']
        self.status_colors = RGB_CONFIG['STATUS_COLORS']
        
        # Turn off all LEDs initially
        self.clear()
        print("RGB Strip initialized - Pin:" + str(pin) + " LEDs:" + str(num_leds))
        print(f"Config: Brightness={self.default_brightness}, Animation speed={self.animation_speed}ms")
    
    def clear(self):
        """Turn off all LEDs"""
        self.strip.fill((0, 0, 0))
        self.strip.write()
        self.current_status = "off"
    
    def set_led(self, index, red, green, blue):
        """Set individual LED color (0-7, 0-255 for each color)"""
        if 0 <= index < self.num_leds:
            self.strip[index] = (red, green, blue)
            self.strip.write()
    
    def set_all(self, red, green, blue):
        """Set all LEDs to same color"""
        self.strip.fill((red, green, blue))
        self.strip.write()
        self.current_status = "solid_color"
    
    def set_color_name(self, color_name, brightness=128):
        """Set all LEDs to named color"""
        colors = {
            'red': (brightness, 0, 0),
            'green': (0, brightness, 0),
            'blue': (0, 0, brightness),
            'yellow': (brightness, brightness, 0),
            'purple': (brightness, 0, brightness),
            'cyan': (0, brightness, brightness),
            'white': (brightness, brightness, brightness),
            'orange': (brightness, brightness//2, 0),
            'pink': (brightness, brightness//4, brightness//2),
            'off': (0, 0, 0)
        }
        
        color = colors.get(color_name.lower(), (0, 0, 0))
        self.set_all(color[0], color[1], color[2])
        self.current_status = color_name
    
    def progress_bar(self, percent, color=(0, 255, 0)):
        """Show progress bar (0-100%)"""
        self.clear()
        leds_on = int((percent / 100.0) * self.num_leds)
        
        for i in range(leds_on):
            self.strip[i] = color
        self.strip.write()
        self.current_status = "progress_" + str(percent)
    
    def environmental_status(self, env_data):
        """Set LED pattern based on environmental data"""
        if not env_data.get('health_status', False):
            # Sensor error - Red blinking pattern
            self.blink_pattern([0, 2, 4, 6], (255, 0, 0), 3)
            return "sensor_error"
        
        comfort_level = env_data.get('comfort_level', 'unknown')
        temp = env_data.get('readings', {}).get('temperature_c', 0)
        humidity = env_data.get('readings', {}).get('humidity', 0)
        
        if comfort_level == 'comfortable':
            # All green - optimal environment
            self.set_color_name('green')
            return "optimal"
        elif comfort_level in ['too_hot', 'too_cold']:
            # Orange gradient for temperature issues
            self.temperature_gradient(temp)
            return "temperature_warning"
        elif comfort_level in ['too_humid', 'too_dry']:
            # Blue pattern for humidity issues
            self.humidity_pattern(humidity)
            return "humidity_warning"
        else:
            # Blue - unknown/initializing
            self.set_color_name('blue')
            return "unknown"
    
    def temperature_gradient(self, temp):
        """Show temperature as color gradient"""
        self.clear()
        # Cold = Blue, Normal = Green, Hot = Red
        for i in range(self.num_leds):
            if temp < 20:  # Cold
                intensity = max(50, min(255, int((20 - temp) * 20)))
                self.strip[i] = (0, 0, intensity)
            elif temp > 28:  # Hot
                intensity = max(50, min(255, int((temp - 28) * 30)))
                self.strip[i] = (intensity, 0, 0)
            else:  # Normal
                self.strip[i] = (0, 128, 0)
        self.strip.write()
    
    def humidity_pattern(self, humidity):
        """Show humidity as pattern"""
        self.clear()
        leds_on = max(1, min(8, int(humidity / 12.5)))  # 0-100% -> 0-8 LEDs
        
        for i in range(leds_on):
            if humidity < 30:  # Too dry - Red
                self.strip[i] = (128, 0, 0)
            elif humidity > 70:  # Too humid - Blue
                self.strip[i] = (0, 0, 128)
            else:  # Normal - Cyan
                self.strip[i] = (0, 128, 128)
        self.strip.write()
    
    def rainbow_cycle(self, speed=50):
        """Rainbow color cycle effect"""
        colors = [
            (255, 0, 0),    # Red
            (255, 128, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),    # Blue
            (128, 0, 255),  # Purple
            (255, 0, 128)   # Pink
        ]
        
        for i in range(self.num_leds):
            self.strip[i] = colors[i]
        self.strip.write()
        time.sleep_ms(speed)
        
        # Rotate colors
        for shift in range(8):
            for i in range(self.num_leds):
                color_index = (i + shift) % len(colors)
                self.strip[i] = colors[color_index]
            self.strip.write()
            time.sleep_ms(speed)
    
    def blink_pattern(self, led_indices, color, times=3, delay_ms=500):
        """Blink specific LEDs"""
        for _ in range(times):
            self.clear()
            for index in led_indices:
                if 0 <= index < self.num_leds:
                    self.strip[index] = color
            self.strip.write()
            time.sleep_ms(delay_ms)
            
            self.clear()
            time.sleep_ms(delay_ms)
    
    def startup_sequence(self):
        """Show startup animation"""
        print("RGB Strip startup sequence...")
        
        # Fill LEDs one by one
        for i in range(self.num_leds):
            self.strip[i] = (50, 50, 50)
            self.strip.write()
            time.sleep_ms(100)
        
        time.sleep_ms(300)
        
        # Rainbow sweep
        self.rainbow_cycle(100)
        
        # End with green (ready)
        self.set_color_name('green', 100)
        time.sleep_ms(500)
        self.clear()
    
    def system_status(self, wifi_ok=False, camera_ok=False, sensors_ok=False):
        """Show system status across 8 LEDs"""
        self.clear()
        
        # LED 0-2: WiFi status
        wifi_color = (0, 255, 0) if wifi_ok else (255, 0, 0)
        for i in range(3):
            self.strip[i] = wifi_color
        
        # LED 3-5: Camera status
        camera_color = (0, 255, 0) if camera_ok else (255, 0, 0)
        for i in range(3, 6):
            self.strip[i] = camera_color
        
        # LED 6-7: Sensor status
        sensor_color = (0, 255, 0) if sensors_ok else (255, 0, 0)
        for i in range(6, 8):
            self.strip[i] = sensor_color
        
        self.strip.write()
        
        if wifi_ok and camera_ok and sensors_ok:
            return "all_systems_ok"
        else:
            return "system_issues"
    
    def get_status(self):
        """Get current status"""
        return self.current_status
    
    def cleanup(self):
        """Cleanup resources"""
        self.clear() 