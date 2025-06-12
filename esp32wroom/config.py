# ESP32-WROVER Smart Home Configuration
# Central configuration file for all pins, settings, and system parameters

# =============================================================================
# PIN CONFIGURATION
# =============================================================================

# Camera Pins (ESP32-CAM Module)
CAMERA_PINS = {
    'D0': 4,
    'D1': 5,
    'D2': 18,
    'D3': 19,
    'D4': 36,
    'D5': 39,
    'D6': 34,
    'D7': 35,
    'HREF': 23,
    'VSYNC': 25,
    'RESET': -1,  # Not connected
    'PWDN': -1,   # Not connected
    'SIOC': 27,   # I2C Clock for camera
    'SIOD': 26,   # I2C Data for camera
    'XCLK': 21,   # External clock
    'PCLK': 22    # Pixel clock
}

# Smart Home Module Pins
SMART_HOME_PINS = {
    # RGB LED Strip (8 LEDs)
    'RGB_STRIP': 2,
    
    # Environmental Sensors
    'DHT11_SENSOR': 15,
    
    # Alarm System
    'ACTIVE_BUZZER': 32,
    'PASSIVE_BUZZER': 33,
    'STATUS_LED': 0,
    
    # Motion Detection System
    'PIR_SENSOR': 13,        # HC-SR501 PIR motion sensor
    'MOTION_LED': 14,        # LED indicator for motion detection
    
    # PWM Audio System
    'PWM_AUDIO': 12,         # PWM output to FREENOVE audio board
    'AUDIO_STATUS_LED': 0,   # Audio system indicator (built-in LED)
    
    # Available GPIO pins for expansion
    'SPARE_GPIO': [1, 3, 16, 17]  # Available for future modules (updated)
}

# =============================================================================
# WIFI CONFIGURATION
# =============================================================================

WIFI_CONFIG = {
    # Station Mode (Connect to existing router)
    'STA_SSID': "iPhone (188)",
    'STA_PASSWORD': "12345678",
    'STA_TIMEOUT': 15,  # Connection timeout in seconds
    
    # Access Point Mode (Create own hotspot)
    'AP_SSID': "ESP32-CAM",
    'AP_PASSWORD': "12345678",
    'AP_IP': "192.168.4.1",
    'AP_SUBNET': "255.255.255.0",
    'AP_GATEWAY': "192.168.4.1",
    'AP_DNS': "8.8.8.8"
}

# =============================================================================
# CAMERA CONFIGURATION
# =============================================================================

CAMERA_CONFIG = {
    'DEFAULT_SETTINGS': {
        'resolution': 7,  # camera.FRAME_QVGA (we'll handle this in main)
        'quality': 15,    # JPEG quality (lower = better quality)
        'brightness': 0,  # -2 to +2
        'contrast': 0,    # -2 to +2
        'saturation': 0,  # -2 to +2
        'flip': 1,        # 0 or 1
        'mirror': 1       # 0 or 1
    },
    'XCLK_FREQ': 20000000,  # 20MHz external clock
    'FORMAT': 4,  # camera.JPEG
    'FB_LOCATION': 1,  # camera.PSRAM
    'INIT_RETRIES': 3
}

# =============================================================================
# SENSOR CONFIGURATION
# =============================================================================

SENSOR_CONFIG = {
    'DHT11': {
        'READ_INTERVAL': 3000,  # milliseconds between reads
        'ERROR_THRESHOLD': 5,   # max errors before sensor marked as failed
        'COMFORT_ZONES': {
            'temperature_min': 20,  # Celsius
            'temperature_max': 26,  # Celsius
            'humidity_min': 30,     # Percentage
            'humidity_max': 70      # Percentage
        }
    }
}

# =============================================================================
# ALARM SYSTEM CONFIGURATION
# =============================================================================

ALARM_CONFIG = {
    'SNOOZE_DURATION': 9,     # minutes
    'MAX_ALARM_DURATION': 30, # minutes
    'ALARM_TYPES': ['gentle', 'normal', 'urgent'],
    'DEFAULT_ALARM_TYPE': 'gentle',
    'SUNRISE_SIMULATION_DURATION': 300  # seconds (5 minutes)
}

# =============================================================================
# RGB STRIP CONFIGURATION
# =============================================================================

RGB_CONFIG = {
    'NUM_LEDS': 8,
    'DEFAULT_BRIGHTNESS': 128,  # 0-255
    'ANIMATION_SPEED': 50,      # milliseconds
    'STATUS_COLORS': {
        'ready': (0, 255, 0),      # Green
        'error': (255, 0, 0),      # Red
        'warning': (255, 128, 0),  # Orange
        'info': (0, 0, 255),       # Blue
        'off': (0, 0, 0)           # Black
    }
}

# =============================================================================
# WEB SERVER CONFIGURATION
# =============================================================================

WEB_SERVER_CONFIG = {
    'PORT': 80,
    'DEBUG': True,
    'ROUTES': {
        'main': '/',
        'stream': '/stream',
        'video': '/video',
        'capture': '/capture',
        'settings': '/settings',
        'status': '/status',
        'api_sensors': '/api/sensors',
        'api_camera': '/api/camera',
        'api_alarm': '/api/alarm'
    }
}

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

SYSTEM_CONFIG = {
    'DEBUG_MODE': True,
    'LOG_LEVEL': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'MEMORY_CHECK_INTERVAL': 60,  # seconds
    'STATUS_UPDATE_INTERVAL': 5,  # seconds
    'WATCHDOG_TIMEOUT': 30,       # seconds
    'AUTO_RESTART_ON_ERROR': True
}

# =============================================================================
# HARDWARE PROFILES
# =============================================================================

HARDWARE_PROFILES = {
    'ESP32_CAM_AI_THINKER': {
        'camera_model': 'AI_THINKER',
        'psram_available': True,
        'flash_size': '4MB',
        'camera_pins': CAMERA_PINS
    },
    'ESP32_WROVER': {
        'psram_available': True,
        'flash_size': '4MB',
        'extra_ram': '8MB'
    }
}

# Current hardware profile
CURRENT_PROFILE = 'ESP32_CAM_AI_THINKER'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_pin(pin_name, category='SMART_HOME_PINS'):
    """Get pin number by name from configuration"""
    if category == 'CAMERA':
        return CAMERA_PINS.get(pin_name.upper())
    elif category == 'SMART_HOME':
        return SMART_HOME_PINS.get(pin_name.upper())
    return None

def get_camera_pin_config():
    """Get complete camera pin configuration for initialization"""
    return CAMERA_PINS

def get_wifi_config():
    """Get WiFi configuration"""
    return WIFI_CONFIG

def get_system_status():
    """Get system configuration summary"""
    return {
        'hardware_profile': CURRENT_PROFILE,
        'debug_mode': SYSTEM_CONFIG['DEBUG_MODE'],
        'pins_configured': len(SMART_HOME_PINS) + len(CAMERA_PINS),
        'modules_available': ['camera', 'environmental_sensor', 'alarm_system', 'rgb_strip']
    }

def validate_pin_conflicts():
    """Check for pin conflicts between modules"""
    used_pins = []
    conflicts = []
    
    # Collect all used pins
    for pin in CAMERA_PINS.values():
        if pin > 0:  # Skip -1 (not connected)
            used_pins.append(('CAMERA', pin))
    
    for name, pin in SMART_HOME_PINS.items():
        if isinstance(pin, int) and pin > 0:
            used_pins.append(('SMART_HOME', name, pin))
    
    # Check for duplicates
    pin_values = [pin[-1] if isinstance(pin, tuple) else pin for pin in used_pins if isinstance(pin, tuple)]
    seen_pins = set()
    
    for pin_info in used_pins:
        pin_num = pin_info[-1]
        if pin_num in seen_pins:
            conflicts.append(f"Pin {pin_num} conflict: {pin_info}")
        seen_pins.add(pin_num)
    
    return conflicts

# Run validation on import
_pin_conflicts = validate_pin_conflicts()
if _pin_conflicts:
    print("⚠️  PIN CONFLICTS DETECTED:")
    for conflict in _pin_conflicts:
        print(f"   {conflict}")
else:
    print("✅ Pin configuration validated - no conflicts detected") 