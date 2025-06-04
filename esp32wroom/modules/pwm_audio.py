# PWM Audio Module for ESP32-WROVER Smart Home
# Provides audio notifications using PWM and FREENOVE Audio Board

from machine import Pin, PWM
import utime
import math

class PWMAudio:
    """PWM Audio Controller for FREENOVE Audio Board"""
    
    def __init__(self, pwm_pin=12, status_led_pin=0):
        self.pwm_pin = pwm_pin
        self.status_led_pin = status_led_pin
        self.is_enabled = True
        self.current_volume = 256  # Default volume
        self.pwm = None
        self.status_led = None
        
        # Initialize hardware
        try:
            # Initialize PWM (like the working test)
            self.pwm = PWM(Pin(self.pwm_pin))
            self.pwm.freq(1000)
            self.pwm.duty(0)  # Start silent
            print(f"✅ PWM initialized on pin {self.pwm_pin}")
            
            # Initialize status LED (optional)
            if self.status_led_pin is not None:
                try:
                    self.status_led = Pin(self.status_led_pin, Pin.OUT)
                    self.status_led.off()
                    print(f"✅ Status LED initialized on pin {self.status_led_pin}")
                except Exception as e:
                    print(f"⚠️ Status LED init failed: {e}")
                    self.status_led = None
            
            print(f"PWM Audio initialized - PWM: Pin {pwm_pin}, LED: Pin {status_led_pin}")
            self.play_startup_sound()
            
        except Exception as e:
            print(f"PWM Audio initialization error: {e}")
            self.is_enabled = False
    
    def play_startup_sound(self):
        """Play startup melody"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            startup_melody = [
                (440, 0.2),   # A4
                (523, 0.2),   # C5  
                (659, 0.2),   # E5
                (784, 0.4)    # G5 (longer)
            ]
            
            for freq, duration in startup_melody:
                self.play_tone(freq, duration)
                utime.sleep(0.05)  # Small gap between notes
            
            if self.status_led:
                self.status_led.off()
            print("🎵 Startup sound played")
            
        except Exception as e:
            print(f"Startup sound error: {e}")
    
    def play_tone(self, frequency, duration, volume=None):
        """Play a single tone"""
        if not self.is_enabled or not self.pwm:
            return
            
        try:
            if volume is None:
                volume = self.current_volume
                
            self.pwm.freq(int(frequency))
            self.pwm.duty(int(volume))
            utime.sleep(duration)
            self.pwm.duty(0)  # Silent
            
        except Exception as e:
            print(f"Tone play error: {e}")
    
    def play_motion_alert(self):
        """Play motion detection alert sound"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            # Rising tone sequence for motion
            frequencies = [800, 1000, 1200, 1500]
            for freq in frequencies:
                self.play_tone(freq, 0.1, self.current_volume)
            
            if self.status_led:
                self.status_led.off()
            print("🚨 Motion alert sound played")
            
        except Exception as e:
            print(f"Motion alert error: {e}")
    
    def play_photo_capture_sound(self):
        """Play photo capture confirmation sound"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            # Camera shutter sound simulation
            self.play_tone(1200, 0.1, self.current_volume)
            utime.sleep(0.05)
            self.play_tone(800, 0.1, self.current_volume)
            
            if self.status_led:
                self.status_led.off()
            print("📸 Photo capture sound played")
            
        except Exception as e:
            print(f"Photo sound error: {e}")
    
    def play_alarm_sound(self):
        """Play alarm/warning sound"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            # Alternating high-low alarm
            for i in range(3):
                self.play_tone(1000, 0.3, self.current_volume)
                self.play_tone(500, 0.3, self.current_volume)
            
            if self.status_led:
                self.status_led.off()
            print("🚨 Alarm sound played")
            
        except Exception as e:
            print(f"Alarm sound error: {e}")
    
    def play_success_sound(self):
        """Play success confirmation sound"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            # Rising success melody
            success_notes = [
                (523, 0.15),  # C5
                (659, 0.15),  # E5
                (784, 0.25)   # G5
            ]
            
            for freq, duration in success_notes:
                self.play_tone(freq, duration, self.current_volume)
                utime.sleep(0.05)
            
            if self.status_led:
                self.status_led.off()
            print("✅ Success sound played")
            
        except Exception as e:
            print(f"Success sound error: {e}")
    
    def play_error_sound(self):
        """Play error/failure sound"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            # Low error beeps
            for i in range(3):
                self.play_tone(200, 0.2, self.current_volume)
                utime.sleep(0.1)
            
            if self.status_led:
                self.status_led.off()
            print("❌ Error sound played")
            
        except Exception as e:
            print(f"Error sound error: {e}")
    
    def play_notification_beep(self):
        """Play simple notification beep"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            self.play_tone(1000, 0.2, self.current_volume)
            if self.status_led:
                self.status_led.off()
            print("🔔 Notification beep played")
            
        except Exception as e:
            print(f"Notification beep error: {e}")
    
    def play_sweep(self, start_freq=200, end_freq=2000, duration=2.0):
        """Play frequency sweep"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            steps = 50
            step_duration = duration / steps
            
            for i in range(steps):
                freq = start_freq + (end_freq - start_freq) * i / steps
                self.play_tone(freq, step_duration, self.current_volume)
            
            if self.status_led:
                self.status_led.off()
            print(f"🎶 Frequency sweep played ({start_freq}Hz → {end_freq}Hz)")
            
        except Exception as e:
            print(f"Sweep error: {e}")
    
    def play_melody(self, notes):
        """Play a melody from a list of (frequency, duration) tuples"""
        if not self.is_enabled:
            return
            
        try:
            if self.status_led:
                self.status_led.on()
            
            for freq, duration in notes:
                self.play_tone(freq, duration, self.current_volume)
                utime.sleep(0.05)  # Small gap between notes
            
            if self.status_led:
                self.status_led.off()
            print(f"🎵 Melody played ({len(notes)} notes)")
            
        except Exception as e:
            print(f"Melody error: {e}")
    
    def set_volume(self, volume_percent):
        """Set audio volume (0-100%)"""
        try:
            # Convert percentage to duty cycle (0-1023)
            self.current_volume = int((volume_percent / 100.0) * 1023)
            if self.current_volume > 1023:
                self.current_volume = 1023
            elif self.current_volume < 0:
                self.current_volume = 0
                
            print(f"🔊 Volume set to {volume_percent}% (duty: {self.current_volume})")
            
            # Play test tone
            if volume_percent > 0:
                self.play_tone(1000, 0.1, self.current_volume)
            
        except Exception as e:
            print(f"Volume set error: {e}")
    
    def test_audio_system(self):
        """Test all audio functions"""
        if not self.is_enabled:
            print("❌ Audio system not available")
            return False
            
        print("🔧 Testing PWM Audio System...")
        
        try:
            # Test basic tones
            print("   Testing basic tones...")
            test_frequencies = [440, 880, 1000, 500]
            for freq in test_frequencies:
                self.play_tone(freq, 0.3, 300)
                utime.sleep(0.2)
            
            # Test volume levels
            print("   Testing volume levels...")
            for volume in [128, 256, 512, 768]:
                self.play_tone(1000, 0.2, volume)
                utime.sleep(0.1)
            
            # Test notification sounds
            print("   Testing notification sounds...")
            self.play_success_sound()
            utime.sleep(0.5)
            self.play_error_sound()
            utime.sleep(0.5)
            self.play_motion_alert()
            utime.sleep(0.5)
            
            print("✅ Audio system test complete!")
            return True
            
        except Exception as e:
            print(f"❌ Audio test failed: {e}")
            return False
    
    def enable_audio(self):
        """Enable audio notifications"""
        self.is_enabled = True
        self.play_success_sound()
        print("🔊 Audio enabled")
    
    def disable_audio(self):
        """Disable audio notifications"""
        self.is_enabled = False
        if self.pwm:
            self.pwm.duty(0)  # Ensure silence
        if self.status_led:
            self.status_led.off()
        print("🔇 Audio disabled")
    
    def get_audio_status(self):
        """Get current audio system status"""
        return {
            'enabled': self.is_enabled,
            'volume_percent': int((self.current_volume / 1023.0) * 100),
            'volume_duty': self.current_volume,
            'pwm_pin': self.pwm_pin,
            'status_led_pin': self.status_led_pin
        }
    
    def cleanup(self):
        """Cleanup PWM resources"""
        try:
            if self.pwm:
                self.pwm.duty(0)
                self.pwm.deinit()
            if self.status_led:
                self.status_led.off()
            print("PWM Audio cleanup complete")
        except:
            pass

# Predefined melodies for different occasions
MELODIES = {
    'startup': [
        (440, 0.2), (523, 0.2), (659, 0.2), (784, 0.4)
    ],
    'motion_alert': [
        (800, 0.1), (1000, 0.1), (1200, 0.1), (1500, 0.2)
    ],
    'happy_birthday': [
        (262, 0.3), (262, 0.3), (294, 0.6), (262, 0.6),
        (349, 0.6), (330, 1.2)
    ],
    'twinkle_star': [
        (262, 0.4), (262, 0.4), (392, 0.4), (392, 0.4),
        (440, 0.4), (440, 0.4), (392, 0.8)
    ]
} 