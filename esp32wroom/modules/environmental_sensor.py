# Environmental Sensor Module for ESP32-WROVER Smart Home
# Integrates DHT11 temperature/humidity with existing camera server

import sys
sys.path.append('lib')
import dht
from machine import Pin
import time
import gc

class EnvironmentalSensor:
    def __init__(self, dht_pin=15):
        """Initialize environmental sensors"""
        self.dht_sensor = dht.DHT11(Pin(dht_pin))
        self.last_reading_time = 0
        self.reading_interval = 3000  # 3 seconds minimum
        
        # Current readings
        self.temperature_c = 0
        self.humidity = 0
        self.temperature_f = 0
        
        # Status
        self.sensor_status = "initializing"
        self.error_count = 0
        
        print("Environmental sensor initialized on Pin " + str(dht_pin))
    
    def read_sensors(self):
        """Read all environmental sensors"""
        current_time = time.ticks_ms()
        
        # Check if enough time has passed
        if time.ticks_diff(current_time, self.last_reading_time) < self.reading_interval:
            return True  # Return cached values
        
        try:
            # Read DHT11
            self.dht_sensor.measure()
            self.temperature_c = self.dht_sensor.temperature()
            self.humidity = self.dht_sensor.humidity()
            self.temperature_f = round(self.temperature_c * 9.0 / 5.0 + 32.0, 1)
            
            # Update status
            if self.temperature_c > 0 and self.humidity > 0:
                self.sensor_status = "ok"
                self.error_count = 0
                self.last_reading_time = current_time
                return True
            else:
                self.sensor_status = "invalid_reading"
                return False
                
        except Exception as e:
            self.error_count += 1
            self.sensor_status = "error: " + str(e)
            print("Environmental sensor error: " + str(e))
            return False
    
    def get_readings_dict(self):
        """Get readings as dictionary for web interface"""
        # Try to get fresh reading
        self.read_sensors()
        
        return {
            'temperature_c': round(self.temperature_c, 1),
            'temperature_f': round(self.temperature_f, 1),
            'humidity': round(self.humidity, 1),
            'sensor_status': self.sensor_status,
            'error_count': self.error_count,
            'timestamp': time.ticks_ms(),
            'last_update': time.time() if hasattr(time, 'time') else 0
        }
    
    def get_temperature_celsius(self):
        """Get current temperature in Celsius"""
        self.read_sensors()
        return self.temperature_c
    
    def get_temperature_fahrenheit(self):
        """Get current temperature in Fahrenheit"""
        self.read_sensors()
        return self.temperature_f
    
    def get_humidity(self):
        """Get current humidity percentage"""
        self.read_sensors()
        return self.humidity
    
    def get_status(self):
        """Get sensor status"""
        return self.sensor_status
    
    def is_healthy(self):
        """Check if sensors are working properly"""
        return self.sensor_status == "ok" and self.error_count < 5
    
    def get_comfort_level(self):
        """Determine comfort level based on temperature and humidity"""
        if not self.is_healthy():
            return "unknown"
        
        temp = self.temperature_c
        humidity = self.humidity
        
        # Comfort zone logic
        if 20 <= temp <= 26 and 30 <= humidity <= 70:
            return "comfortable"
        elif temp < 18:
            return "too_cold"
        elif temp > 28:
            return "too_hot"
        elif humidity < 30:
            return "too_dry"
        elif humidity > 70:
            return "too_humid"
        else:
            return "moderate"
    
    def get_environmental_summary(self):
        """Get comprehensive environmental summary"""
        readings = self.get_readings_dict()
        comfort = self.get_comfort_level()
        
        return {
            'readings': readings,
            'comfort_level': comfort,
            'recommendations': self._get_recommendations(comfort),
            'health_status': self.is_healthy()
        }
    
    def _get_recommendations(self, comfort_level):
        """Get recommendations based on comfort level"""
        recommendations = {
            'comfortable': 'Environment is optimal!',
            'too_cold': 'Consider increasing temperature',
            'too_hot': 'Consider cooling or ventilation',
            'too_dry': 'Consider using humidifier',
            'too_humid': 'Consider dehumidification',
            'moderate': 'Environment is acceptable',
            'unknown': 'Check sensor connections'
        }
        
        return recommendations.get(comfort_level, 'No recommendations available')
    
    def cleanup(self):
        """Cleanup resources"""
        gc.collect() 