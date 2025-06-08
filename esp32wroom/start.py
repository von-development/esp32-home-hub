# ESP32-WROVER Smart Home System - Quick Start Script
# Run this file to start the complete smart home system

print("🏠 ESP32 Smart Home System - Quick Start")
print("==========================================")

try:
    # Import and run the main system
    from esp32wroom.main import main
    main()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Make sure all modules are in the correct directory")
    
except Exception as e:
    print(f"❌ System error: {e}")
    print("🔄 Try restarting the ESP32")

print("✅ Smart Home System stopped") 