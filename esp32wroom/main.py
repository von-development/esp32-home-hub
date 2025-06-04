# ESP32-WROVER Smart Home System - Main Controller
# Organized main file using configuration system and modular architecture

import sys
import gc
import utime
import camera
import network
import ulogging as logging

# Import configuration
from config import (
    WIFI_CONFIG, CAMERA_CONFIG, SYSTEM_CONFIG, 
    get_camera_pin_config, get_system_status
)

# Import modules
sys.path.append('modules')
import web_server
from environmental_sensor import EnvironmentalSensor
from alarm_system import SmartAlarmSystem
from rgb_strip import RGBStrip
from motion_detector import MotionDetector
from pwm_audio import PWMAudio

# Import pins from config
from config import SMART_HOME_PINS

class SmartHomeSystem:
    def __init__(self):
        """Initialize the complete Smart Home System"""
        self.system_name = "ESP32-WROVER Smart Home"
        self.version = "2.0.0"
        self.start_time = utime.time()
        
        # System components
        self.wifi_sta = None
        self.wifi_ap = None
        self.camera_initialized = False
        self.web_server = None
        
        # Smart home modules
        self.env_sensor = None
        self.alarm_system = None
        self.rgb_strip = None
        self.motion_detector = None
        self.pwm_audio = None
        
        # System status
        self.system_status = {
            'wifi_sta_ok': False,
            'wifi_ap_ok': False,
            'camera_ok': False,
            'sensors_ok': False,
            'alarm_ok': False,
            'rgb_ok': False,
            'motion_ok': False,
            'audio_ok': False,
            'web_server_ok': False
        }
        
        print(f"🚀 Initializing {self.system_name} v{self.version}")
        print("=" * 50)
    
    def initialize_wifi(self):
        """Initialize WiFi in dual mode (STA + AP)"""
        print("📡 Setting up WiFi connections...")
        
        try:
            # Clean up any existing connections
            try:
                temp_sta = network.WLAN(network.STA_IF)
                temp_ap = network.WLAN(network.AP_IF)
                if temp_sta.active():
                    temp_sta.disconnect()
                    temp_sta.active(False)
                if temp_ap.active():
                    temp_ap.active(False)
                utime.sleep(0.5)
            except:
                pass
            
            # Setup Access Point
            self.wifi_ap = network.WLAN(network.AP_IF)
            self.wifi_ap.active(False)
            utime.sleep(0.1)
            
            # Configure AP with settings from config
            ap_config = [
                WIFI_CONFIG['AP_IP'],
                WIFI_CONFIG['AP_SUBNET'],
                WIFI_CONFIG['AP_GATEWAY'],
                WIFI_CONFIG['AP_DNS']
            ]
            self.wifi_ap.ifconfig(ap_config)
            self.wifi_ap.active(True)
            self.wifi_ap.config(
                essid=WIFI_CONFIG['AP_SSID'],
                authmode=network.AUTH_WPA_WPA2_PSK,
                password=WIFI_CONFIG['AP_PASSWORD']
            )
            utime.sleep(1)
            
            if self.wifi_ap.active():
                self.system_status['wifi_ap_ok'] = True
                print(f"✅ AP Mode: {WIFI_CONFIG['AP_SSID']} - IP: {self.wifi_ap.ifconfig()[0]}")
            
            # Setup Station Mode
            self.wifi_sta = network.WLAN(network.STA_IF)
            self.wifi_sta.active(False)
            utime.sleep(0.1)
            self.wifi_sta.active(True)
            
            if not self.wifi_sta.isconnected():
                print(f"🔄 Connecting to {WIFI_CONFIG['STA_SSID']}...")
                self.wifi_sta.connect(WIFI_CONFIG['STA_SSID'], WIFI_CONFIG['STA_PASSWORD'])
                
                timeout = WIFI_CONFIG['STA_TIMEOUT']
                while not self.wifi_sta.isconnected() and timeout > 0:
                    utime.sleep(1)
                    timeout -= 1
                
                if self.wifi_sta.isconnected():
                    self.system_status['wifi_sta_ok'] = True
                    print(f"✅ STA Mode: Connected - IP: {self.wifi_sta.ifconfig()[0]}")
                else:
                    print("⚠️  STA connection failed - AP mode still available")
            
        except Exception as e:
            print(f"❌ WiFi setup error: {e}")
            return False
        
        return True
    
    def initialize_camera(self):
        """Initialize camera with configuration settings"""
        print("📷 Initializing camera...")
        
        retries = CAMERA_CONFIG['INIT_RETRIES']
        
        for attempt in range(retries):
            try:
                # Deinitialize if already initialized
                camera.deinit()
                utime.sleep(0.1)
                
                # Get camera pins from config
                pins = get_camera_pin_config()
                
                # Initialize with config settings using proper camera constants
                camera.init(
                    0,  # Camera ID
                    d0=pins['D0'], d1=pins['D1'], d2=pins['D2'], d3=pins['D3'],
                    d4=pins['D4'], d5=pins['D5'], d6=pins['D6'], d7=pins['D7'],
                    format=camera.JPEG,  # Use camera constant
                    xclk_freq=camera.XCLK_20MHz,  # Use camera constant
                    href=pins['HREF'], vsync=pins['VSYNC'],
                    reset=pins['RESET'], pwdn=pins['PWDN'],
                    sioc=pins['SIOC'], siod=pins['SIOD'],
                    xclk=pins['XCLK'], pclk=pins['PCLK'],
                    fb_location=camera.PSRAM  # Use camera constant
                )
                
                # Apply default settings
                self._apply_camera_settings()
                
                # Test capture
                test_buf = camera.capture()
                if test_buf:
                    del test_buf
                    self.camera_initialized = True
                    self.system_status['camera_ok'] = True
                    print("✅ Camera initialized successfully")
                    return True
                
            except Exception as e:
                print(f"⚠️  Camera init attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    utime.sleep(1)
        
        print("❌ Camera initialization failed after all attempts")
        return False
    
    def _apply_camera_settings(self):
        """Apply camera settings from configuration"""
        settings = CAMERA_CONFIG['DEFAULT_SETTINGS']
        
        camera.framesize(camera.FRAME_QVGA)  # Use camera constant
        camera.quality(settings['quality'])
        camera.brightness(settings['brightness'])
        camera.contrast(settings['contrast'])
        camera.saturation(settings['saturation'])
        camera.flip(settings['flip'])
        camera.mirror(settings['mirror'])
    
    def initialize_sensors(self):
        """Initialize environmental sensors"""
        print("🌡️  Initializing environmental sensors...")
        
        try:
            self.env_sensor = EnvironmentalSensor(
                dht_pin=SMART_HOME_PINS['DHT11_SENSOR']
            )
            
            # Test sensor reading
            if self.env_sensor.read_sensors():
                self.system_status['sensors_ok'] = True
                temp = self.env_sensor.get_temperature_celsius()
                humidity = self.env_sensor.get_humidity()
                print(f"✅ Environmental sensor ready - {temp}°C, {humidity}%RH")
                return True
            else:
                print("⚠️  Environmental sensor test reading failed")
                
        except Exception as e:
            print(f"❌ Environmental sensor error: {e}")
        
        return False
    
    def initialize_rgb_strip(self):
        """Initialize RGB LED strip"""
        print("🌈 Initializing RGB LED strip...")
        
        try:
            self.rgb_strip = RGBStrip(
                pin=SMART_HOME_PINS['RGB_STRIP'],
                num_leds=8
            )
            
            # Test RGB strip
            self.rgb_strip.startup_sequence()
            self.system_status['rgb_ok'] = True
            print("✅ RGB LED strip initialized")
            return True
            
        except Exception as e:
            print(f"❌ RGB strip error: {e}")
            return False
    
    def initialize_alarm_system(self):
        """Initialize smart alarm system"""
        print("⏰ Initializing alarm system...")
        
        try:
            self.alarm_system = SmartAlarmSystem(
                active_buzzer_pin=SMART_HOME_PINS['ACTIVE_BUZZER'],
                passive_buzzer_pin=SMART_HOME_PINS['PASSIVE_BUZZER'],
                status_led_pin=SMART_HOME_PINS['STATUS_LED'],
                environmental_sensor=self.env_sensor,
                rgb_strip=self.rgb_strip
            )
            
            # Set initial time (example - you'd normally get this from NTP)
            self.alarm_system.set_time(2024, 1, 1, 12, 0, 0)
            
            self.system_status['alarm_ok'] = True
            print("✅ Alarm system initialized")
            return True
            
        except Exception as e:
            print(f"❌ Alarm system error: {e}")
            return False
    
    def initialize_motion_detector(self):
        """Initialize PIR motion detection system"""
        print("🚶 Initializing motion detection system...")
        
        try:
            self.motion_detector = MotionDetector(
                pir_pin=SMART_HOME_PINS['PIR_SENSOR'],
                motion_led_pin=SMART_HOME_PINS['MOTION_LED']
            )
            
            self.system_status['motion_ok'] = True
            print("✅ Motion detector initialized")
            return True
            
        except Exception as e:
            print(f"❌ Motion detector error: {e}")
            return False
    
    def initialize_pwm_audio(self):
        """Initialize PWM audio system"""
        print("🔊 Initializing PWM audio system...")
        
        try:
            self.pwm_audio = PWMAudio(
                pwm_pin=SMART_HOME_PINS['PWM_AUDIO'],
                status_led_pin=SMART_HOME_PINS['AUDIO_STATUS_LED']
            )
            
            self.system_status['audio_ok'] = True
            print("✅ PWM audio initialized")
            return True
            
        except Exception as e:
            print(f"❌ PWM audio error: {e}")
            return False
    
    def initialize_web_server(self):
        """Initialize web server with all modules"""
        print("🌐 Initializing web server...")
        
        try:
            # Initialize the web server modules with our components
            web_server.init_modules(
                environmental_sensor=self.env_sensor,
                alarm_sys=self.alarm_system,
                rgb_controller=self.rgb_strip,
                motion_detector_sys=self.motion_detector,
                audio_system=self.pwm_audio
            )
            
            self.system_status['web_server_ok'] = True
            print("✅ Web server initialized")
            return True
            
        except Exception as e:
            print(f"❌ Web server error: {e}")
            return False
    
    def display_system_status(self):
        """Display comprehensive system status"""
        print("\n" + "=" * 50)
        print(f"🏠 {self.system_name} - System Status")
        print("=" * 50)
        
        # System info
        uptime = int((utime.time() - self.start_time) / 60)
        print(f"⏱️  Uptime: {uptime} minutes")
        print(f"💾 Free Memory: {gc.mem_free()} bytes")
        
        # Network status
        print(f"📡 WiFi STA: {'✅' if self.system_status['wifi_sta_ok'] else '❌'}")
        print(f"📡 WiFi AP:  {'✅' if self.system_status['wifi_ap_ok'] else '❌'}")
        
        # Hardware status
        print(f"📷 Camera:   {'✅' if self.system_status['camera_ok'] else '❌'}")
        print(f"🌡️  Sensors:  {'✅' if self.system_status['sensors_ok'] else '❌'}")
        print(f"⏰ Alarm:    {'✅' if self.system_status['alarm_ok'] else '❌'}")
        print(f"🌈 RGB Strip:{'✅' if self.system_status['rgb_ok'] else '❌'}")
        print(f"🚶 Motion:   {'✅' if self.system_status['motion_ok'] else '❌'}")
        print(f"🔊 Audio:    {'✅' if self.system_status['audio_ok'] else '❌'}")
        print(f"🌐 Web Server:{'✅' if self.system_status['web_server_ok'] else '❌'}")
        
        # Access information
        if self.system_status['wifi_ap_ok']:
            print(f"\n🔗 Access Points:")
            print(f"   AP Mode: http://{self.wifi_ap.ifconfig()[0]}")
        
        if self.system_status['wifi_sta_ok']:
            print(f"   STA Mode: http://{self.wifi_sta.ifconfig()[0]}")
        
        print("=" * 50)
    
    def update_system_status(self):
        """Update RGB strip with system status"""
        if self.rgb_strip:
            self.rgb_strip.system_status(
                wifi_ok=self.system_status['wifi_sta_ok'] or self.system_status['wifi_ap_ok'],
                camera_ok=self.system_status['camera_ok'],
                sensors_ok=self.system_status['sensors_ok']
            )
    
    def run_system_loop(self):
        """Main system loop with motion detection"""
        last_status_update = 0
        last_alarm_check = 0
        last_motion_check = 0
        
        print("🔄 Starting main system loop...")
        
        while True:
            try:
                current_time = utime.time()
                
                # Check motion detection every 100ms
                if self.motion_detector and current_time - last_motion_check > 0.1:
                    if self.motion_detector.check_motion():
                        # Motion detected - play audio alert
                        if self.pwm_audio:
                            self.pwm_audio.play_motion_alert()
                        # Trigger RGB indication
                        if self.rgb_strip:
                            self.rgb_strip.set_color_name('red', 255)
                            utime.sleep_ms(100)
                            self.rgb_strip.clear()
                    last_motion_check = current_time
                
                # Update system status every 30 seconds
                if current_time - last_status_update > 30:
                    self.update_system_status()
                    gc.collect()  # Memory cleanup
                    last_status_update = current_time
                
                # Check alarm system every minute
                if self.alarm_system and current_time - last_alarm_check > 60:
                    self.alarm_system.update()
                    last_alarm_check = current_time
                
                # Brief sleep to prevent watchdog timeout
                utime.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n🛑 System shutdown requested")
                break
            except Exception as e:
                print(f"❌ System loop error: {e}")
                utime.sleep(5)  # Wait before retrying
    
    def start_web_server(self):
        """Start the web server"""
        try:
            print("🌐 Starting web server...")
            web_server.run_server(
                host="0.0.0.0",
                port=80,
                debug=SYSTEM_CONFIG['DEBUG_MODE']
            )
        except Exception as e:
            print(f"❌ Web server start error: {e}")
    
    def initialize_all(self):
        """Initialize all system components"""
        success_count = 0
        total_components = 8  # Updated to include motion detector and PWM audio
        
        # Initialize components in order
        if self.initialize_wifi():
            success_count += 1
        
        if self.initialize_camera():
            success_count += 1
        
        if self.initialize_sensors():
            success_count += 1
        
        if self.initialize_rgb_strip():
            success_count += 1
        
        if self.initialize_alarm_system():
            success_count += 1
        
        if self.initialize_motion_detector():
            success_count += 1
        
        if self.initialize_pwm_audio():
            success_count += 1
        
        if self.initialize_web_server():
            success_count += 1
        
        # Display final status
        self.display_system_status()
        
        print(f"\n🎯 System initialization: {success_count}/{total_components} components ready")
        
        if success_count >= 5:  # Minimum viable system (updated threshold)
            print("✅ System ready to start!")
            
            # Play success sound
            if self.pwm_audio:
                self.pwm_audio.play_success_sound()
            
            return True
        else:
            print("❌ Critical components failed - system cannot start")
            
            # Play error sound
            if self.pwm_audio:
                self.pwm_audio.play_error_sound()
            
            return False


def main():
    """Main function"""
    print("🚀 ESP32-WROVER Smart Home System Starting...")
    
    # Create system instance
    smart_home = SmartHomeSystem()
    
    try:
        # Initialize all components
        if smart_home.initialize_all():
            
            # Show RGB startup indication
            if smart_home.rgb_strip:
                smart_home.rgb_strip.set_color_name('green', 100)
                utime.sleep(1)
                smart_home.rgb_strip.clear()
            
            # Start web server (this will block)
            smart_home.start_web_server()
        else:
            print("❌ System initialization failed")
            
            # Show error on RGB strip
            if smart_home.rgb_strip:
                smart_home.rgb_strip.set_color_name('red', 100)
            
    except Exception as e:
        print(f"❌ Critical system error: {e}")
        
        # Show error indication
        if smart_home.rgb_strip:
            smart_home.rgb_strip.blink_pattern([0, 2, 4, 6], (255, 0, 0), 5)
    
    finally:
        print("🛑 System shutdown")


if __name__ == "__main__":
    main() 