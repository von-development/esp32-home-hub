#!/usr/bin/env python3
"""
ESP32-WROVER Smart Home Deployment Script
Validates configuration and helps organize files for deployment
"""

import os
import sys

def check_file_exists(filepath):
    """Check if file exists and return status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return True, f"✅ {filepath} ({size} bytes)"
    else:
        return False, f"❌ {filepath} - NOT FOUND"

def validate_project_structure():
    """Validate the project structure"""
    print("🔍 Validating ESP32-WROVER Smart Home Project Structure")
    print("=" * 60)
    
    required_files = [
        "config.py",
        "main_new.py",
        "README.md",
        "modules/web_server.py",
        "modules/environmental_sensor.py",
        "modules/alarm_system.py",
        "modules/rgb_strip.py",
        "lib/pwm_buzzer.py",
        "lib/neopixel.py",
        "lib/dht.py",
        "lib/ulogging.py"
    ]
    
    optional_files = [
        "main.py",  # Legacy file
        "lib/pkg_resources.py",
        "tests/test_sd_card.py",
        "tests/test_i2s_audio.py"
    ]
    
    all_good = True
    
    print("📋 Required Files:")
    for file in required_files:
        exists, status = check_file_exists(file)
        print(f"   {status}")
        if not exists:
            all_good = False
    
    print("\n📦 Optional Files:")
    for file in optional_files:
        exists, status = check_file_exists(file)
        print(f"   {status}")
    
    return all_good

def validate_configuration():
    """Validate the configuration file"""
    print("\n⚙️  Validating Configuration")
    print("=" * 30)
    
    try:
        # Import and test config
        sys.path.append('.')
        import config
        
        # Check pin conflicts
        conflicts = config.validate_pin_conflicts()
        if conflicts:
            print("❌ Pin conflicts detected:")
            for conflict in conflicts:
                print(f"   {conflict}")
            return False
        else:
            print("✅ No pin conflicts detected")
        
        # Check WiFi config
        wifi_config = config.get_wifi_config()
        if wifi_config['STA_SSID'] == "Avenida":
            print("⚠️  Using default WiFi credentials - update config.py")
        else:
            print("✅ WiFi credentials configured")
        
        # Check system status
        system_status = config.get_system_status()
        print(f"✅ System config: {system_status['pins_configured']} pins configured")
        print(f"✅ Hardware profile: {system_status['hardware_profile']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Config validation error: {e}")
        return False

def generate_deployment_commands():
    """Generate ampy commands for deployment"""
    print("\n🚀 Deployment Commands")
    print("=" * 30)
    
    commands = [
        "# Upload configuration",
        "ampy put config.py",
        "",
        "# Upload main application",
        "ampy put main_new.py",
        "",
        "# Create and upload modules",
        "ampy mkdir modules",
        "ampy put modules/web_server.py modules/",
        "ampy put modules/environmental_sensor.py modules/",
        "ampy put modules/alarm_system.py modules/",
        "ampy put modules/rgb_strip.py modules/",
        "",
        "# Upload required libraries",
        "ampy put lib/pwm_buzzer.py lib/",
        "ampy put lib/neopixel.py lib/",
        "ampy put lib/dht.py lib/",
        "ampy put lib/ulogging.py lib/",
        "",
        "# Replace main file (after testing)",
        "# ampy rm main.py",
        "# ampy put main_new.py main.py",
        "",
        "# Optional: Upload tests",
        "# ampy mkdir tests",
        "# ampy put tests/ tests/",
    ]
    
    print("Copy and run these commands with ampy:")
    print()
    for cmd in commands:
        print(cmd)

def create_deployment_summary():
    """Create a deployment summary"""
    print("\n📊 Deployment Summary")
    print("=" * 30)
    
    # Count files by type
    core_files = 0
    module_files = 0
    lib_files = 0
    test_files = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                if 'modules/' in root:
                    module_files += 1
                elif 'lib/' in root:
                    lib_files += 1
                elif 'tests/' in root:
                    test_files += 1
                elif root == '.':
                    core_files += 1
    
    print(f"📁 Core files: {core_files}")
    print(f"🧩 Module files: {module_files}")
    print(f"📚 Library files: {lib_files}")
    print(f"🧪 Test files: {test_files}")
    print(f"📦 Total Python files: {core_files + module_files + lib_files + test_files}")
    
    # Memory estimate
    total_size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                total_size += os.path.getsize(os.path.join(root, file))
    
    print(f"💾 Estimated flash usage: {total_size} bytes ({total_size/1024:.1f} KB)")

def main():
    """Main deployment validation function"""
    print("🚀 ESP32-WROVER Smart Home - Deployment Validator")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Validate structure
    structure_ok = validate_project_structure()
    
    # Validate configuration
    config_ok = validate_configuration()
    
    # Generate deployment info
    create_deployment_summary()
    
    if structure_ok and config_ok:
        print("\n✅ Project validation successful!")
        generate_deployment_commands()
        
        print("\n🔧 Next Steps:")
        print("1. Connect ESP32 via USB")
        print("2. Run ampy commands above")
        print("3. Test with main_new.py first")
        print("4. Replace main.py when confirmed working")
        print("5. Access web interface via WiFi")
        
    else:
        print("\n❌ Project validation failed!")
        print("Fix the issues above before deployment.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 