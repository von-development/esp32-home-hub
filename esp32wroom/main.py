# ESP32-WROVER Advanced Camera Server with Picoweb Framework
# Dual WiFi Mode (STA + AP) with PSRAM support

import picoweb
import utime
import camera
import gc
import network
import ulogging as logging

# WiFi Configuration
SSID_ROUTER = "Avenida"
PASSWORD_ROUTER = "Avenida2024"
SSID_AP = "ESP32-CAM"
PASSWORD_AP = "12345678"
LOCAL_IP = "192.168.4.1"
SUBNET = "255.255.255.0"
GATEWAY = "192.168.4.1"
DNS = "8.8.8.8"

# Global variables
sta_if = None
ap_if = None
camera_settings = {
    'resolution': camera.FRAME_QVGA,
    'quality': 15,
    'brightness': 0,
    'contrast': 0,
    'saturation': 0,
    'flip': 1,
    'mirror': 1
}

def wifi_setup():
    """Setup dual WiFi mode (STA + AP)"""
    global sta_if, ap_if
    
    # Clean up existing connections
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
    
    # Setup AP mode
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    utime.sleep(0.1)
    ap_if.ifconfig([LOCAL_IP, SUBNET, GATEWAY, DNS])  # Fixed order
    ap_if.active(True)
    ap_if.config(essid=SSID_AP, authmode=network.AUTH_WPA_WPA2_PSK, password=PASSWORD_AP)
    utime.sleep(1)
    print("AP Mode: " + SSID_AP + " - IP: " + ap_if.ifconfig()[0])
    
    # Setup STA mode
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    utime.sleep(0.1)
    sta_if.active(True)
    
    if not sta_if.isconnected():
        print("Connecting to " + SSID_ROUTER + "...")
        sta_if.connect(SSID_ROUTER, PASSWORD_ROUTER)
        timeout = 15
        while not sta_if.isconnected() and timeout > 0:
            utime.sleep(1)
            timeout -= 1
        
        if sta_if.isconnected():
            print("STA Mode: Connected - IP: " + sta_if.ifconfig()[0])
        else:
            print("STA connection failed")

def camera_init():
    """Initialize camera with PSRAM"""
    try:
        camera.deinit()
        camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                    format=camera.JPEG, xclk_freq=camera.XCLK_20MHz,
                    href=23, vsync=25, reset=-1, pwdn=-1,
                    sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)
        
        apply_camera_settings()
        print("Camera initialized with PSRAM")
        return True
    except Exception as e:
        print("Camera init failed: " + str(e))
        return False

def apply_camera_settings():
    """Apply current camera settings"""
    camera.framesize(camera_settings['resolution'])
    camera.quality(camera_settings['quality'])
    camera.brightness(camera_settings['brightness'])
    camera.contrast(camera_settings['contrast'])
    camera.saturation(camera_settings['saturation'])
    camera.flip(camera_settings['flip'])
    camera.mirror(camera_settings['mirror'])

# HTML Templates

MAIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Server</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .nav { display: flex; justify-content: center; margin: 20px 0; }
        .nav a { margin: 0 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
        .nav a:hover { background: #45a049; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .status { display: flex; justify-content: space-around; margin: 20px 0; }
        .status div { text-align: center; padding: 10px; background: #f9f9f9; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🚀 ESP32-WROVER Camera Server</h1>
        
        <div class="nav">
            <a href="/stream">📹 Live Stream</a>
            <a href="/capture">📸 Capture Photo</a>
            <a href="/settings">⚙️ Settings</a>
            <a href="/status">📊 Status</a>
        </div>
        
        <div class="info">
            <h3>📡 Network Information</h3>
            <div class="status">
                <div><strong>STA Mode</strong><br>%s</div>
                <div><strong>AP Mode</strong><br>%s</div>
            </div>
        </div>
        
        <div class="info">
            <h3>🎯 Quick Access</h3>
            <p><strong>Live Stream:</strong> <a href="/stream">Real-time camera feed</a></p>
            <p><strong>Photo Capture:</strong> <a href="/capture">Take high-resolution photos</a></p>
            <p><strong>Settings:</strong> <a href="/settings">Adjust camera parameters</a></p>
            <p><strong>Status:</strong> <a href="/status">System information</a></p>
        </div>
    </div>
</body>
</html>"""

STREAM_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Live Stream</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #000; color: white; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; }
        img { max-width: 100%%; height: auto; border: 2px solid #4CAF50; border-radius: 10px; }
        .controls { margin: 20px 0; }
        .controls a { margin: 0 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
        .controls a:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📹 Live Camera Stream</h1>
        <img src="/video" alt="Camera Stream">
        <div class="controls">
            <a href="/">🏠 Home</a>
            <a href="/capture">📸 Capture</a>
            <a href="/settings">⚙️ Settings</a>
        </div>
    </div>
</body>
</html>"""

SETTINGS_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Camera Settings</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .setting { margin: 15px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }
        .setting label { display: block; margin-bottom: 5px; font-weight: bold; }
        .setting input, .setting select { width: 100%%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .button:hover { background: #45a049; }
        .nav a { margin: 0 10px; padding: 10px 20px; background: #666; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ Camera Settings</h1>
        
        <form method="POST" action="/settings">
            <div class="setting">
                <label>Quality (10=best, 63=worst):</label>
                <input type="range" name="quality" min="10" max="63" value="%d">
            </div>
            
            <div class="setting">
                <label>Brightness (-2 to 2):</label>
                <input type="range" name="brightness" min="-2" max="2" value="%d">
            </div>
            
            <div class="setting">
                <label>Contrast (-2 to 2):</label>
                <input type="range" name="contrast" min="-2" max="2" value="%d">
            </div>
            
            <div class="setting">
                <label>Saturation (-2 to 2):</label>
                <input type="range" name="saturation" min="-2" max="2" value="%d">
            </div>
            
            <div class="setting">
                <label>Flip Image:</label>
                <select name="flip">
                    <option value="0"%s>No</option>
                    <option value="1"%s>Yes</option>
                </select>
            </div>
            
            <div class="setting">
                <label>Mirror Image:</label>
                <select name="mirror">
                    <option value="0"%s>No</option>
                    <option value="1"%s>Yes</option>
                </select>
            </div>
            
            <div class="setting">
                <button type="submit" class="button">💾 Save Settings</button>
            </div>
        </form>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" class="nav">🏠 Home</a>
            <a href="/stream" class="nav">📹 Stream</a>
            <a href="/status" class="nav">📊 Status</a>
        </div>
    </div>
</body>
</html>"""

# Route Handlers

def index(req, resp):
    """Main page handler"""
    sta_info = "Connected: " + sta_if.ifconfig()[0] if sta_if and sta_if.isconnected() else "Disconnected"
    ap_info = "Active: " + ap_if.ifconfig()[0] if ap_if and ap_if.active() else "Inactive"
    
    content = MAIN_PAGE % (sta_info, ap_info)
    yield from picoweb.start_response(resp)
    yield from resp.awrite(content)

def stream_page(req, resp):
    """Stream page handler"""
    yield from picoweb.start_response(resp)
    yield from resp.awrite(STREAM_PAGE)

def send_frame():
    """Camera frame generator"""
    try:
        buf = camera.capture()
        if buf:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n'
                   + buf + b'\r\n')
            del buf
            gc.collect()
    except Exception as e:
        print("Capture error: " + str(e))
        
def video_stream(req, resp):
    """Video stream handler"""
    yield from picoweb.start_response(resp, content_type="multipart/x-mixed-replace; boundary=frame")
    while True:
        frame_gen = send_frame()
        try:
            frame_data = next(frame_gen)
            yield from resp.awrite(frame_data)
            gc.collect()
            utime.sleep_ms(50)  # ~20 FPS
        except StopIteration:
            break
        except Exception as e:
            print("Stream error: " + str(e))
            break

def settings_handler(req, resp):
    """Settings page handler"""
    if req.method == "POST":
        # Handle form submission
        try:
            yield from req.read_form_data()
            
            # Update camera settings
            if 'quality' in req.form:
                camera_settings['quality'] = int(req.form['quality'])
            if 'brightness' in req.form:
                camera_settings['brightness'] = int(req.form['brightness'])
            if 'contrast' in req.form:
                camera_settings['contrast'] = int(req.form['contrast'])
            if 'saturation' in req.form:
                camera_settings['saturation'] = int(req.form['saturation'])
            if 'flip' in req.form:
                camera_settings['flip'] = int(req.form['flip'])
            if 'mirror' in req.form:
                camera_settings['mirror'] = int(req.form['mirror'])
            
            # Apply settings
            apply_camera_settings()
            
            # Redirect to success
            yield from picoweb.start_response(resp, status="302", headers={"Location": "/settings?saved=1"})
            return
            
        except Exception as e:
            print("Settings error: " + str(e))
    
    # Show settings form
    flip_selected = [" selected" if camera_settings['flip'] == 0 else "", " selected" if camera_settings['flip'] == 1 else ""]
    mirror_selected = [" selected" if camera_settings['mirror'] == 0 else "", " selected" if camera_settings['mirror'] == 1 else ""]
    
    content = SETTINGS_PAGE % (
        camera_settings['quality'],
        camera_settings['brightness'],
        camera_settings['contrast'],
        camera_settings['saturation'],
        flip_selected[0], flip_selected[1],
        mirror_selected[0], mirror_selected[1]
    )
    
    yield from picoweb.start_response(resp)
    yield from resp.awrite(content)

def capture_handler(req, resp):
    """Photo capture handler"""
    try:
        # Temporarily set high quality for photo
        old_quality = camera_settings['quality']
        camera.quality(10)  # Best quality
        
        buf = camera.capture()
        
        # Restore original quality
        camera.quality(old_quality)
        
        if buf:
            yield from picoweb.start_response(resp, content_type="image/jpeg", 
                                            headers={"Content-Disposition": "attachment; filename=esp32_photo.jpg"})
            yield from resp.awrite(buf)
            del buf
            gc.collect()
        else:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite("Capture failed")
            
    except Exception as e:
        print("Capture error: " + str(e))
        yield from picoweb.start_response(resp, status="500")
        yield from resp.awrite("Error: " + str(e))

def status_handler(req, resp):
    """Status page handler"""
    import micropython
    
    # Gather system info
    mem_info = str(gc.mem_free()) + " bytes free"
    
    content = """<!DOCTYPE html>
<html>
<head><title>System Status</title></head>
<body style="font-family: Arial; margin: 20px;">
<h1>📊 System Status</h1>
<p><strong>Memory:</strong> %s</p>
<p><strong>STA Status:</strong> %s</p>
<p><strong>AP Status:</strong> %s</p>
<p><strong>Camera Settings:</strong> Quality=%d, Brightness=%d</p>
<a href="/">🏠 Home</a>
</body>
</html>""" % (
        mem_info,
        "Connected" if sta_if and sta_if.isconnected() else "Disconnected",
        "Active" if ap_if and ap_if.active() else "Inactive",
        camera_settings['quality'],
        camera_settings['brightness']
    )
    
    yield from picoweb.start_response(resp)
    yield from resp.awrite(content)

# URL Routes
ROUTES = [
    ("/", index),
    ("/stream", stream_page),
    ("/video", video_stream),
    ("/settings", settings_handler),
    ("/capture", capture_handler),
    ("/status", status_handler),
]

def main():
    """Main application"""
    print("🚀 ESP32-WROVER Advanced Camera Server Starting...")
    
    # Initialize camera
    if not camera_init():
        print("❌ Camera initialization failed!")
        return
    
    # Setup WiFi
    wifi_setup()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run web application
    print("🌐 Starting Picoweb server...")
    app = picoweb.WebApp(__name__, ROUTES)
    app.run(debug=1, port=80, host="0.0.0.0")

if __name__ == '__main__':
    main() 