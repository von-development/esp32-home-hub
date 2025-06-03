# Test Freenove 8-RGB-LED Strip
# Comprehensive test for all 8 addressable RGB LEDs

from modules.rgb_strip import RGBStrip
import time

print("Freenove 8-RGB-LED Strip Test")
print("=============================")
print("Testing 8 addressable RGB LEDs...")
print("Connection: VCC->3.3V, GND->GND, DIN->Pin2")
print("")

# Initialize RGB strip
rgb_strip = RGBStrip(pin=2, num_leds=8)

try:
    print("1. Testing startup sequence...")
    rgb_strip.startup_sequence()
    time.sleep(2)
    
    print("2. Testing individual LED control...")
    rgb_strip.clear()
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
    
    for i, color in enumerate(colors):
        print("   LED " + str(i) + ": " + str(color))
        rgb_strip.set_led(i, color[0], color[1], color[2])
        time.sleep(0.5)
    
    time.sleep(2)
    
    print("3. Testing color names...")
    color_names = ['red', 'green', 'blue', 'yellow', 'purple', 'cyan', 'white', 'orange']
    
    for color_name in color_names:
        print("   All LEDs: " + color_name)
        rgb_strip.set_color_name(color_name)
        time.sleep(1)
    
    print("4. Testing brightness levels...")
    for brightness in [50, 100, 150, 200, 255]:
        print("   Green brightness: " + str(brightness))
        rgb_strip.set_color_name('green', brightness)
        time.sleep(1)
    
    print("5. Testing progress bar...")
    for percent in range(0, 101, 25):
        print("   Progress: " + str(percent) + "%")
        rgb_strip.progress_bar(percent, (0, 200, 0))
        time.sleep(1)
    
    print("6. Testing rainbow cycle...")
    print("   Rainbow animation (watch the colors move!)")
    rgb_strip.rainbow_cycle(150)
    time.sleep(1)
    
    print("7. Testing environmental status simulation...")
    env_conditions = [
        {
            "health_status": True, 
            "comfort_level": "comfortable",
            "readings": {"temperature_c": 25, "humidity": 50}
        },
        {
            "health_status": True,
            "comfort_level": "too_hot", 
            "readings": {"temperature_c": 32, "humidity": 45}
        },
        {
            "health_status": True,
            "comfort_level": "too_humid",
            "readings": {"temperature_c": 24, "humidity": 80}
        },
        {
            "health_status": False,
            "comfort_level": "unknown",
            "readings": {"temperature_c": 0, "humidity": 0}
        }
    ]
    
    for condition in env_conditions:
        status = rgb_strip.environmental_status(condition)
        print("   " + condition["comfort_level"] + " -> " + status)
        time.sleep(3)
    
    print("8. Testing system status display...")
    system_tests = [
        (True, True, True, "All systems OK"),
        (False, True, True, "No WiFi"),
        (True, False, True, "Camera issue"),
        (True, True, False, "Sensor problem"),
        (False, False, False, "Multiple issues")
    ]
    
    for wifi, camera, sensors, description in system_tests:
        status = rgb_strip.system_status(wifi, camera, sensors)
        print("   " + description + " -> " + status)
        time.sleep(2)
    
    print("9. Testing blink patterns...")
    print("   Even LEDs blinking red")
    rgb_strip.blink_pattern([0, 2, 4, 6], (255, 0, 0), 3, 400)
    time.sleep(1)
    
    print("   Odd LEDs blinking green") 
    rgb_strip.blink_pattern([1, 3, 5, 7], (0, 255, 0), 3, 400)
    time.sleep(1)
    
    print("10. Final test - All LEDs WHITE then OFF")
    rgb_strip.set_color_name('white', 150)
    time.sleep(2)
    rgb_strip.clear()
    
    print("\n✅ SUCCESS! All 8 RGB LEDs working perfectly!")
    print("✅ Ready for Smart Home integration!")
    
except KeyboardInterrupt:
    print("\nTest stopped by user")
except Exception as e:
    print("Test error: " + str(e))
finally:
    rgb_strip.cleanup()

print("\nRGB Strip test completed!")
print("\nIf all LEDs lit up in different colors, your 8-RGB-LED module is working perfectly!")
print("You can now use it for amazing Smart Home visual feedback! 🌈") 