# PIR Motion Detection Module for ESP32-WROVER Smart Home
# Handles motion detection, automatic photo capture, and local storage

from machine import Pin
import utime
import camera
import gc
import uos

class PhotoStorage:
    """Manages local photo storage with rotation"""
    
    def __init__(self, max_photos=6, storage_path='/photos'):
        self.max_photos = max_photos
        self.storage_path = storage_path
        self.photo_count = 0
        self.setup_storage()
    
    def setup_storage(self):
        """Initialize storage directory"""
        try:
            # Try to create photos directory
            try:
                uos.mkdir(self.storage_path)
                print(f"Created photos directory: {self.storage_path}")
            except OSError:
                pass  # Directory already exists
            
            # Count existing photos
            try:
                files = uos.listdir(self.storage_path)
                self.photo_count = len([f for f in files if f.startswith('motion_') and f.endswith('.jpg')])
                print(f"Found {self.photo_count} existing motion photos")
            except:
                self.photo_count = 0
                
        except Exception as e:
            print(f"Storage setup error: {e}")
            # Fallback to RAM storage
            self.storage_path = None
    
    def save_photo(self, photo_data):
        """Save photo with automatic rotation"""
        if not photo_data:
            return None
            
        try:
            # Generate filename with timestamp
            timestamp = utime.localtime()
            filename = f"motion_{timestamp[0]:04d}{timestamp[1]:02d}{timestamp[2]:02d}_{timestamp[3]:02d}{timestamp[4]:02d}{timestamp[5]:02d}.jpg"
            
            if self.storage_path:
                # Save to flash storage
                filepath = f"{self.storage_path}/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(photo_data)
                
                self.photo_count += 1
                
                # Rotate photos if limit exceeded
                if self.photo_count > self.max_photos:
                    self._rotate_photos()
                
                print(f"Motion photo saved: {filename} ({len(photo_data)} bytes)")
                return filepath
            else:
                # RAM storage (limited)
                print(f"Photo captured in RAM: {filename} ({len(photo_data)} bytes)")
                return f"RAM:{filename}"
                
        except Exception as e:
            print(f"Photo save error: {e}")
            return None
    
    def _rotate_photos(self):
        """Delete oldest photos when limit exceeded"""
        try:
            if not self.storage_path:
                return
                
            files = uos.listdir(self.storage_path)
            motion_files = [f for f in files if f.startswith('motion_') and f.endswith('.jpg')]
            motion_files.sort()  # Sort by filename (timestamp)
            
            # Delete oldest files
            while len(motion_files) > self.max_photos:
                oldest_file = motion_files.pop(0)
                uos.remove(f"{self.storage_path}/{oldest_file}")
                print(f"Deleted old photo: {oldest_file}")
                self.photo_count -= 1
                
        except Exception as e:
            print(f"Photo rotation error: {e}")
    
    def get_photo_list(self):
        """Get list of stored photos"""
        try:
            if not self.storage_path:
                return []
                
            files = uos.listdir(self.storage_path)
            motion_files = [f for f in files if f.startswith('motion_') and f.endswith('.jpg')]
            motion_files.sort(reverse=True)  # Newest first
            return motion_files
        except:
            return []
    
    def get_storage_info(self):
        """Get storage statistics"""
        return {
            'photo_count': self.photo_count,
            'max_photos': self.max_photos,
            'storage_path': self.storage_path,
            'storage_type': 'flash' if self.storage_path else 'ram'
        }

class MotionDetector:
    """PIR Motion Detection with automatic photo capture"""
    
    def __init__(self, pir_pin=13, motion_led_pin=14):
        self.pir_pin = pir_pin
        self.motion_led_pin = motion_led_pin
        self.last_motion_time = 0
        self.motion_cooldown = 5000  # 5 seconds between captures
        self.motion_count = 0
        self.is_armed = True
        
        # Initialize hardware
        self.pir = Pin(self.pir_pin, Pin.IN)
        self.motion_led = Pin(self.motion_led_pin, Pin.OUT)
        self.motion_led.off()
        
        # Initialize photo storage
        self.photo_storage = PhotoStorage()
        
        # Motion detection state
        self.last_pir_state = 0
        self.motion_active = False
        self.warmup_complete = False
        
        # Start warmup
        self.start_warmup()
        
        print(f"Motion detector initialized - PIR: Pin {pir_pin}, LED: Pin {motion_led_pin}")
    
    def start_warmup(self):
        """Start PIR sensor warmup period"""
        print("PIR sensor warming up (30 seconds)...")
        self.warmup_start = utime.ticks_ms()
        self.warmup_complete = False
        
        # Flash LED during warmup
        for i in range(6):
            self.motion_led.on()
            utime.sleep_ms(200)
            self.motion_led.off()
            utime.sleep_ms(200)
    
    def check_motion(self):
        """Check for motion and handle detection"""
        current_time = utime.ticks_ms()
        
        # Check if warmup is complete
        if not self.warmup_complete:
            if utime.ticks_diff(current_time, self.warmup_start) > 30000:  # 30 seconds
                self.warmup_complete = True
                print("PIR sensor warmup complete - motion detection active")
            return False
        
        if not self.is_armed:
            return False
        
        # Read PIR sensor
        current_pir_state = self.pir.value()
        
        # Detect motion (rising edge)
        if current_pir_state == 1 and self.last_pir_state == 0:
            # Motion started
            if utime.ticks_diff(current_time, self.last_motion_time) > self.motion_cooldown:
                self.motion_count += 1
                self.last_motion_time = current_time
                self.motion_active = True
                
                print(f"🚨 MOTION DETECTED! (Count: {self.motion_count})")
                
                # Turn on motion LED
                self.motion_led.on()
                
                # Capture photo
                photo_path = self.capture_motion_photo()
                
                # Schedule LED off
                self._schedule_led_off(2000)  # 2 seconds
                
                self.last_pir_state = current_pir_state
                return True
        
        elif current_pir_state == 0 and self.last_pir_state == 1:
            # Motion ended
            if self.motion_active:
                print("✅ Motion ended")
                self.motion_active = False
        
        self.last_pir_state = current_pir_state
        return False
    
    def capture_motion_photo(self):
        """Capture photo when motion is detected"""
        try:
            print("📸 Capturing motion photo...")
            
            # Set high quality for motion photos
            old_quality = camera.quality()
            camera.quality(10)  # Best quality
            
            # Capture photo
            photo_data = camera.capture()
            
            # Restore original quality
            camera.quality(old_quality)
            
            if photo_data:
                # Save photo
                photo_path = self.photo_storage.save_photo(photo_data)
                
                # Clean up memory
                del photo_data
                gc.collect()
                
                return photo_path
            else:
                print("❌ Failed to capture motion photo")
                return None
                
        except Exception as e:
            print(f"Motion photo capture error: {e}")
            return None
    
    def _schedule_led_off(self, delay_ms):
        """Schedule LED to turn off after delay"""
        # Simple implementation - in real system might use timer
        def turn_off_led():
            utime.sleep_ms(delay_ms)
            self.motion_led.off()
        
        # For now, just turn off after delay
        utime.sleep_ms(delay_ms)
        self.motion_led.off()
    
    def arm_motion_detection(self):
        """Enable motion detection"""
        self.is_armed = True
        print("🔒 Motion detection ARMED")
    
    def disarm_motion_detection(self):
        """Disable motion detection"""
        self.is_armed = False
        self.motion_led.off()
        print("🔓 Motion detection DISARMED")
    
    def test_motion_led(self):
        """Test the motion LED"""
        print("Testing motion LED...")
        for i in range(3):
            self.motion_led.on()
            utime.sleep_ms(200)
            self.motion_led.off()
            utime.sleep_ms(200)
        print("Motion LED test complete")
    
    def get_motion_status(self):
        """Get current motion detection status"""
        return {
            'armed': self.is_armed,
            'motion_active': self.motion_active,
            'motion_count': self.motion_count,
            'warmup_complete': self.warmup_complete,
            'last_motion_time': self.last_motion_time,
            'storage_info': self.photo_storage.get_storage_info(),
            'photo_list': self.photo_storage.get_photo_list()
        }
    
    def get_recent_photos(self, count=3):
        """Get list of recent motion photos"""
        photos = self.photo_storage.get_photo_list()
        return photos[:count] if photos else []
    
    def cleanup(self):
        """Cleanup resources"""
        self.motion_led.off()
        print("Motion detector cleanup complete") 