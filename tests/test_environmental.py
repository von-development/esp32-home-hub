# Test Environmental Sensor Module
# Standalone test for DHT11 integration module

from modules.environmental_sensor import EnvironmentalSensor
import time
import gc

print("Environmental Sensor Module Test")
print("================================")
print("Testing environmental_sensor.py module...")
print("")

# Initialize environmental sensor
env_sensor = EnvironmentalSensor(dht_pin=15)

try:
    for test_round in range(5):
        print("--- Test Round " + str(test_round + 1) + " ---")
        
        # Test individual functions
        print("Testing individual readings...")
        temp_c = env_sensor.get_temperature_celsius()
        temp_f = env_sensor.get_temperature_fahrenheit()
        humidity = env_sensor.get_humidity()
        status = env_sensor.get_status()
        
        print("Temperature (C): " + str(temp_c))
        print("Temperature (F): " + str(temp_f))
        print("Humidity: " + str(humidity) + "%")
        print("Status: " + status)
        print("Healthy: " + str(env_sensor.is_healthy()))
        
        # Test dictionary output (for web interface)
        print("\nTesting web interface format...")
        readings_dict = env_sensor.get_readings_dict()
        print("Readings Dict: " + str(readings_dict))
        
        # Test comfort level
        comfort = env_sensor.get_comfort_level()
        print("Comfort Level: " + comfort)
        
        # Test comprehensive summary
        print("\nTesting environmental summary...")
        summary = env_sensor.get_environmental_summary()
        print("Summary: " + str(summary))
        
        # Memory check
        print("Free memory: " + str(gc.mem_free()) + " bytes")
        
        print("\nWaiting 5 seconds...\n")
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nTest stopped by user")
except Exception as e:
    print("Test error: " + str(e))
finally:
    env_sensor.cleanup()

print("Environmental module test completed!")
print("If this works, ready for camera server integration!") 