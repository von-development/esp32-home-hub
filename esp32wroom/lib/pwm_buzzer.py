# PWM Buzzer Library for ESP32-WROVER Smart Home Alarm System
# Supports both Active and Passive buzzers with tone generation

from machine import Pin, PWM
import time

class PWMBuzzer:
    def __init__(self, pin):
        """Initialize buzzer on specified pin"""
        self.pin = Pin(pin, Pin.OUT)
        self.pwm = None
        self.is_active = False
        
        # Musical note frequencies (Hz)
        self.notes = {
            'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392, 'A4': 440, 'B4': 494,
            'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698, 'G5': 784, 'A5': 880, 'B5': 988,
            'REST': 0
        }
        
        print(f"PWM Buzzer initialized on Pin {pin}")
    
    def start_tone(self, frequency=1000, duty=512):
        """Start playing a tone at specified frequency"""
        try:
            if self.pwm:
                self.pwm.deinit()
            
            if frequency > 0:
                self.pwm = PWM(self.pin, freq=frequency)
                self.pwm.duty(duty)  # 50% duty cycle (512/1024)
                self.is_active = True
            else:
                self.stop()
        except Exception as e:
            print(f"Buzzer tone error: {e}")
    
    def stop(self):
        """Stop the buzzer"""
        try:
            if self.pwm:
                self.pwm.deinit()
                self.pwm = None
            self.pin.off()
            self.is_active = False
        except Exception as e:
            print(f"Buzzer stop error: {e}")
    
    def beep(self, frequency=1000, duration_ms=200, duty=512):
        """Single beep with specified duration"""
        self.start_tone(frequency, duty)
        time.sleep_ms(duration_ms)
        self.stop()
    
    def play_note(self, note, duration_ms=500):
        """Play a musical note"""
        if note in self.notes:
            frequency = self.notes[note]
            if frequency > 0:
                self.start_tone(frequency)
                time.sleep_ms(duration_ms)
                self.stop()
            else:
                time.sleep_ms(duration_ms)  # Rest note
    
    def play_melody(self, melody, note_duration=300, pause_duration=50):
        """Play a sequence of notes"""
        for note in melody:
            self.play_note(note, note_duration)
            time.sleep_ms(pause_duration)
    
    def alarm_pattern_1(self, duration_seconds=5):
        """Classic alarm pattern: high-low alternating"""
        end_time = time.ticks_ms() + (duration_seconds * 1000)
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            self.beep(1500, 500)  # High tone
            time.sleep_ms(100)
            self.beep(800, 500)   # Low tone
            time.sleep_ms(100)
    
    def alarm_pattern_2(self, duration_seconds=5):
        """Urgent alarm pattern: rapid beeps"""
        end_time = time.ticks_ms() + (duration_seconds * 1000)
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            for _ in range(3):
                self.beep(2000, 150)
                time.sleep_ms(50)
            time.sleep_ms(300)
    
    def alarm_pattern_3(self, duration_seconds=5):
        """Gentle wake-up pattern: ascending tones"""
        end_time = time.ticks_ms() + (duration_seconds * 1000)
        frequencies = [400, 500, 600, 700, 800, 900, 1000]
        
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            for freq in frequencies:
                self.beep(freq, 200)
                time.sleep_ms(50)
            time.sleep_ms(500)
    
    def play_wake_up_melody(self):
        """Play a pleasant wake-up melody"""
        melody = ['C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4']
        self.play_melody(melody, 400, 100)
    
    def play_alarm_melody(self):
        """Play urgent alarm melody"""
        melody = ['A5', 'A5', 'A5', 'A5', 'REST', 'A5', 'A5', 'A5', 'A5']
        self.play_melody(melody, 200, 50)
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()

class ActiveBuzzer:
    def __init__(self, pin):
        """Initialize active buzzer (simple on/off)"""
        self.pin = Pin(pin, Pin.OUT)
        self.pin.off()
        print(f"Active Buzzer initialized on Pin {pin}")
    
    def on(self):
        """Turn buzzer on"""
        self.pin.on()
    
    def off(self):
        """Turn buzzer off"""
        self.pin.off()
    
    def beep(self, duration_ms=200):
        """Simple beep"""
        self.on()
        time.sleep_ms(duration_ms)
        self.off()
    
    def alarm_beeps(self, count=5, duration=200, pause=200):
        """Multiple alarm beeps"""
        for _ in range(count):
            self.beep(duration)
            time.sleep_ms(pause)
    
    def cleanup(self):
        """Clean up resources"""
        self.off() 