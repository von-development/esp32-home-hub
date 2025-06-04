# Smart Alarm System Module for ESP32-WROVER Smart Home
# Integrates buzzers, LEDs, environmental sensors for intelligent wake-up

import sys
sys.path.append('lib')
sys.path.append('..')  # To access config
from pwm_buzzer import PWMBuzzer, ActiveBuzzer
from machine import Pin, RTC
import time
import gc

# Import configuration
try:
    from config import SMART_HOME_PINS, ALARM_CONFIG
except ImportError:
    # Fallback if config not available
    SMART_HOME_PINS = {
        'ACTIVE_BUZZER': 32,
        'PASSIVE_BUZZER': 33,
        'STATUS_LED': 0
    }
    ALARM_CONFIG = {
        'SNOOZE_DURATION': 9,
        'MAX_ALARM_DURATION': 30,
        'ALARM_TYPES': ['gentle', 'normal', 'urgent'],
        'DEFAULT_ALARM_TYPE': 'gentle',
        'SUNRISE_SIMULATION_DURATION': 300
    }

class SmartAlarmSystem:
    def __init__(self, active_buzzer_pin=None, passive_buzzer_pin=None, 
                 status_led_pin=None, environmental_sensor=None, rgb_strip=None):
        """Initialize Smart Alarm System"""
        
        # Use config pins if not specified
        if active_buzzer_pin is None:
            active_buzzer_pin = SMART_HOME_PINS['ACTIVE_BUZZER']
        if passive_buzzer_pin is None:
            passive_buzzer_pin = SMART_HOME_PINS['PASSIVE_BUZZER']
        if status_led_pin is None:
            status_led_pin = SMART_HOME_PINS['STATUS_LED']
        
        # Audio components
        self.active_buzzer = ActiveBuzzer(active_buzzer_pin)
        self.passive_buzzer = PWMBuzzer(passive_buzzer_pin)
        
        # Visual indicators
        self.status_led = Pin(status_led_pin, Pin.OUT)
        self.status_led.off()
        
        # Integration with existing systems
        self.env_sensor = environmental_sensor
        self.rgb_strip = rgb_strip
        
        # Alarm state
        self.alarm_active = False
        self.alarm_time = None  # (hour, minute)
        self.snooze_time = None
        self.alarm_enabled = False
        
        # Configuration from config.py
        self.snooze_duration = ALARM_CONFIG['SNOOZE_DURATION']
        self.max_alarm_duration = ALARM_CONFIG['MAX_ALARM_DURATION']
        self.current_alarm_type = ALARM_CONFIG['DEFAULT_ALARM_TYPE']
        self.sunrise_duration = ALARM_CONFIG['SUNRISE_SIMULATION_DURATION']
        
        # RTC for time keeping
        self.rtc = RTC()
        
        # Alarm timing
        self.alarm_start_time = None
        
        print("Smart Alarm System initialized")
        print(f"Active Buzzer: Pin {active_buzzer_pin}")
        print(f"Passive Buzzer: Pin {passive_buzzer_pin}")
        print(f"Status LED: Pin {status_led_pin}")
        print(f"Config: Snooze={self.snooze_duration}min, Max duration={self.max_alarm_duration}min")
    
    def set_time(self, year, month, day, hour, minute, second=0):
        """Set current time"""
        self.rtc.datetime((year, month, day, 0, hour, minute, second, 0))
        print(f"Time set to: {hour:02d}:{minute:02d}")
    
    def get_time(self):
        """Get current time as (hour, minute, second)"""
        dt = self.rtc.datetime()
        return (dt[4], dt[5], dt[6])  # hour, minute, second
    
    def get_time_string(self):
        """Get formatted time string"""
        hour, minute, second = self.get_time()
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def set_alarm(self, hour, minute, alarm_type="gentle"):
        """Set alarm time and type"""
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            self.alarm_time = (hour, minute)
            self.alarm_enabled = True
            self.current_alarm_type = alarm_type
            print(f"Alarm set for {hour:02d}:{minute:02d} ({alarm_type} mode)")
            return True
        else:
            print("Invalid time format")
            return False
    
    def disable_alarm(self):
        """Disable the alarm"""
        self.alarm_enabled = False
        self.alarm_active = False
        self.snooze_time = None
        self.stop_alarm()
        print("Alarm disabled")
    
    def snooze_alarm(self):
        """Snooze the alarm for specified duration"""
        if self.alarm_active:
            self.stop_alarm()
            current_time = self.get_time()
            # Calculate snooze time
            snooze_minutes = (current_time[1] + self.snooze_duration) % 60
            snooze_hours = (current_time[0] + (current_time[1] + self.snooze_duration) // 60) % 24
            self.snooze_time = (snooze_hours, snooze_minutes)
            print(f"Alarm snoozed until {snooze_hours:02d}:{snooze_minutes:02d}")
    
    def check_alarm_trigger(self):
        """Check if alarm should be triggered"""
        if not self.alarm_enabled:
            return False
        
        current_time = self.get_time()
        current_hour, current_minute = current_time[0], current_time[1]
        
        # Check main alarm
        if self.alarm_time and not self.alarm_active:
            alarm_hour, alarm_minute = self.alarm_time
            if current_hour == alarm_hour and current_minute == alarm_minute:
                self.trigger_alarm()
                return True
        
        # Check snooze alarm
        if self.snooze_time and not self.alarm_active:
            snooze_hour, snooze_minute = self.snooze_time
            if current_hour == snooze_hour and current_minute == snooze_minute:
                self.trigger_alarm()
                self.snooze_time = None  # Clear snooze
                return True
        
        return False
    
    def trigger_alarm(self):
        """Start the alarm sequence"""
        self.alarm_active = True
        self.alarm_start_time = time.ticks_ms()
        self.status_led.on()
        
        print(f"🚨 ALARM TRIGGERED! ({self.current_alarm_type} mode)")
        
        # Start sunrise simulation if RGB strip available
        if self.rgb_strip:
            self.start_sunrise_simulation()
        
        # Start audio alarm based on type
        if self.current_alarm_type == "gentle":
            self.gentle_wake_up_sequence()
        elif self.current_alarm_type == "normal":
            self.normal_alarm_sequence()
        elif self.current_alarm_type == "urgent":
            self.urgent_alarm_sequence()
    
    def gentle_wake_up_sequence(self):
        """Gentle wake-up with progressive volume/intensity"""
        print("Starting gentle wake-up sequence...")
        # Start with passive buzzer melody
        try:
            self.passive_buzzer.play_wake_up_melody()
        except Exception as e:
            print(f"Passive buzzer error: {e}")
            # Fallback to active buzzer
            self.active_buzzer.beep(500)
    
    def normal_alarm_sequence(self):
        """Standard alarm sequence"""
        print("Starting normal alarm sequence...")
        try:
            self.passive_buzzer.alarm_pattern_1(3)
        except Exception as e:
            print(f"Passive buzzer error: {e}")
            self.active_buzzer.alarm_beeps(5)
    
    def urgent_alarm_sequence(self):
        """Urgent alarm sequence"""
        print("Starting urgent alarm sequence...")
        try:
            self.passive_buzzer.alarm_pattern_2(5)
        except Exception as e:
            print(f"Passive buzzer error: {e}")
            self.active_buzzer.alarm_beeps(10, 100, 100)
    
    def start_sunrise_simulation(self):
        """Simulate sunrise with RGB LEDs"""
        if not self.rgb_strip:
            return
        
        print("Starting sunrise simulation...")
        try:
            # Gradually increase brightness over 5 minutes
            for brightness in range(0, 256, 8):
                # Warm sunrise colors: red -> orange -> yellow -> white
                if brightness < 64:
                    # Early sunrise - red/orange
                    red = brightness * 4
                    green = brightness // 2
                    blue = 0
                elif brightness < 128:
                    # Mid sunrise - orange/yellow
                    red = 255
                    green = brightness * 2
                    blue = 0
                else:
                    # Full daylight - white
                    red = 255
                    green = 255
                    blue = brightness - 128
                
                self.rgb_strip.set_all(red, green, blue)
                time.sleep_ms(300)  # Gradual change
                
        except Exception as e:
            print(f"Sunrise simulation error: {e}")
    
    def stop_alarm(self):
        """Stop all alarm sounds and visuals"""
        self.alarm_active = False
        self.status_led.off()
        
        # Stop all audio
        try:
            self.active_buzzer.off()
            self.passive_buzzer.stop()
        except Exception as e:
            print(f"Error stopping alarm: {e}")
        
        print("Alarm stopped")
    
    def check_auto_stop(self):
        """Auto-stop alarm after maximum duration"""
        if self.alarm_active and self.alarm_start_time:
            elapsed = time.ticks_diff(time.ticks_ms(), self.alarm_start_time)
            if elapsed > (self.max_alarm_duration * 60 * 1000):  # Convert to ms
                print("Alarm auto-stopped after maximum duration")
                self.stop_alarm()
                return True
        return False
    
    def get_weather_adjustment(self):
        """Get wake-up time adjustment based on weather"""
        if not self.env_sensor:
            return 0
        
        try:
            readings = self.env_sensor.get_readings_dict()
            temp = readings.get('temperature_c', 20)
            humidity = readings.get('humidity', 50)
            
            # Wake up earlier if it's cold/wet (need more time to prepare)
            adjustment = 0
            if temp < 15:  # Cold weather
                adjustment += 10  # 10 minutes earlier
            if humidity > 80:  # High humidity/rain
                adjustment += 5   # 5 minutes earlier
            
            return adjustment
        except Exception as e:
            print(f"Weather adjustment error: {e}")
            return 0
    
    def get_alarm_info(self):
        """Get current alarm information"""
        return {
            'enabled': self.alarm_enabled,
            'time': f"{self.alarm_time[0]:02d}:{self.alarm_time[1]:02d}" if self.alarm_time else None,
            'type': self.current_alarm_type,
            'active': self.alarm_active,
            'snooze_time': f"{self.snooze_time[0]:02d}:{self.snooze_time[1]:02d}" if self.snooze_time else None,
            'current_time': self.get_time_string()
        }
    
    def update(self):
        """Main update loop - call this regularly"""
        self.check_alarm_trigger()
        self.check_auto_stop()
        gc.collect()
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_alarm()
        self.active_buzzer.cleanup()
        self.passive_buzzer.cleanup()
        self.status_led.off() 