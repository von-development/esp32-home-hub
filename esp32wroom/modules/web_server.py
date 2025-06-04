# Web Server Module for ESP32-WROVER Smart Home
# Handles all web routes, templates, and HTTP functionality

import picoweb
import utime
import camera
import gc
import json
import network

# Camera settings (global like main.py)
camera_settings = {
    'resolution': camera.FRAME_QVGA,
    'quality': 15,
    'brightness': 0,
    'contrast': 0,
    'saturation': 0,
    'flip': 1,
    'mirror': 1
}

# Global references to modules
env_sensor = None
alarm_system = None
rgb_strip = None
motion_detector = None
pwm_audio = None
server_status = {
    'start_time': utime.time(),
    'requests_handled': 0,
    'errors_count': 0
}

def init_modules(environmental_sensor=None, alarm_sys=None, rgb_controller=None, motion_detector_sys=None, audio_system=None):
    """Initialize module references"""
    global env_sensor, alarm_system, rgb_strip, motion_detector, pwm_audio
    env_sensor = environmental_sensor
    alarm_system = alarm_sys
    rgb_strip = rgb_controller
    motion_detector = motion_detector_sys
    pwm_audio = audio_system
    print("Web server modules initialized")
    print(f"  Motion detector: {'✅' if motion_detector else '❌'}")
    print(f"  PWM audio: {'✅' if pwm_audio else '❌'}")

def apply_camera_settings():
    """Apply current camera settings"""
    camera.framesize(camera_settings['resolution'])
    camera.quality(camera_settings['quality'])
    camera.brightness(camera_settings['brightness'])
    camera.contrast(camera_settings['contrast'])
    camera.saturation(camera_settings['saturation'])
    camera.flip(camera_settings['flip'])
    camera.mirror(camera_settings['mirror'])

def get_network_info():
    """Get network information for display"""
    sta_info = "Not connected"
    ap_info = "Not active"
    
    try:
        sta_if = network.WLAN(network.STA_IF)
        if sta_if.active() and sta_if.isconnected():
            sta_info = f"Connected - IP: {sta_if.ifconfig()[0]}"
    except:
        pass
    
    try:
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_info = f"Active - IP: {ap_if.ifconfig()[0]}"
    except:
        pass
    
    return sta_info, ap_info

# =============================================================================
# HTML TEMPLATES (Enhanced with all components)
# =============================================================================

MAIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Casa Inteligente</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .card { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }
        .nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .nav-card { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; padding: 30px; border-radius: 15px; text-decoration: none; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
        .nav-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,0,0,0.2); }
        .nav-card h3 { font-size: 1.3em; margin-bottom: 10px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .status-item { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; }
        .status-item h4 { color: #333; margin-bottom: 8px; }
        .sensor-data { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }
        .sensor-item { text-align: center; padding: 20px; background: linear-gradient(45deg, #2196F3, #21CBF3); color: white; border-radius: 10px; }
        .control-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .control-panel { background: #fff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .control-panel h3 { margin-bottom: 15px; color: #333; }
        .btn { background: linear-gradient(45deg, #FF6B6B, #FF8E53); color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; margin: 5px; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .btn.green { background: linear-gradient(45deg, #4CAF50, #45a049); }
        .btn.blue { background: linear-gradient(45deg, #2196F3, #21CBF3); }
        .btn.purple { background: linear-gradient(45deg, #9C27B0, #E91E63); }
        .btn.red { background: linear-gradient(45deg, #f44336, #e57373); }
        .color-picker { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 10px 0; }
        .color-btn { width: 40px; height: 40px; border-radius: 50%; border: 3px solid white; cursor: pointer; transition: transform 0.2s; }
        .color-btn:hover { transform: scale(1.1); }
        .slider-container { margin: 10px 0; }
        .slider { width: 100%; height: 8px; border-radius: 5px; background: #ddd; outline: none; }
        .alarm-status { padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin: 10px 0; }
        .alarm-armed { background: #ffebee; color: #c62828; }
        .alarm-disarmed { background: #e8f5e8; color: #2e7d32; }
        .footer { text-align: center; color: rgba(255,255,255,0.8); margin-top: 30px; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Casa Inteligente ESP32</h1>
            <p>Servidor de Câmera Avançado com Monitoramento Ambiental</p>
        </div>
        
        <div class="nav-grid">
            <a href="/stream" class="nav-card">
                <h3>Transmissão ao Vivo</h3>
                <p>Feed da câmera em tempo real</p>
            </a>
            <a href="/capture" class="nav-card">
                <h3>Capturar Foto</h3>
                <p>Captura de imagem em alta resolução</p>
            </a>
            <a href="/settings" class="nav-card">
                <h3>Configurações</h3>
                <p>Ajustar resolução, qualidade e mais</p>
            </a>
            <a href="/status" class="nav-card">
                <h3>Status do Sistema</h3>
                <p>Monitorar saúde e desempenho</p>
            </a>
        </div>
        
        <div class="card">
            <h3>Status da Rede</h3>
            <div class="status-grid">
                <div class="status-item">
                    <h4>Modo Estação</h4>
                    <p>STA_INFO_PLACEHOLDER</p>
                </div>
                <div class="status-item">
                    <h4>Ponto de Acesso</h4>
                    <p>AP_INFO_PLACEHOLDER</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Dados Ambientais</h3>
            <div class="sensor-data" id="sensorData">
                <div class="sensor-item">
                    <h4>Temperatura</h4>
                    <p id="temp">Carregando...</p>
                </div>
                <div class="sensor-item">
                    <h4>Umidade</h4>
                    <p id="humidity">Carregando...</p>
                </div>
                <div class="sensor-item">
                    <h4>Nível de Conforto</h4>
                    <p id="comfort">Carregando...</p>
                </div>
            </div>
        </div>
        
        <div class="control-grid">
            <div class="control-panel">
                <h3>Controle de LEDs RGB</h3>
                <div id="rgbStatus" class="alarm-status alarm-disarmed">Status: Carregando...</div>
                
                <div class="color-picker">
                    <div class="color-btn" style="background: #FF0000;" onclick="setRGBColor(255,0,0)" title="Vermelho"></div>
                    <div class="color-btn" style="background: #00FF00;" onclick="setRGBColor(0,255,0)" title="Verde"></div>
                    <div class="color-btn" style="background: #0000FF;" onclick="setRGBColor(0,0,255)" title="Azul"></div>
                    <div class="color-btn" style="background: #FFFF00;" onclick="setRGBColor(255,255,0)" title="Amarelo"></div>
                    <div class="color-btn" style="background: #FF00FF;" onclick="setRGBColor(255,0,255)" title="Magenta"></div>
                    <div class="color-btn" style="background: #00FFFF;" onclick="setRGBColor(0,255,255)" title="Ciano"></div>
                    <div class="color-btn" style="background: #FFFFFF;" onclick="setRGBColor(255,255,255)" title="Branco"></div>
                    <div class="color-btn" style="background: #000000;" onclick="setRGBColor(0,0,0)" title="Desligar"></div>
                </div>
                
                <div class="slider-container">
                    <label>Brilho: <span id="brightnessValue">50</span>%%</label>
                    <input type="range" class="slider" id="brightnessSlider" min="0" max="100" value="50" onchange="setBrightness()">
                </div>
                
                <button class="btn green" onclick="rgbPattern('rainbow')">Arco-íris</button>
                <button class="btn blue" onclick="rgbPattern('breathing')">Respiração</button>
                <button class="btn purple" onclick="rgbPattern('startup')">Inicialização</button>
                <button class="btn red" onclick="rgbOff()">DESLIGAR</button>
            </div>
            
            <div class="control-panel">
                <h3>Sistema de Segurança</h3>
                <div id="alarmStatus" class="alarm-status alarm-disarmed">Status: Carregando...</div>
                
                <button class="btn red" id="armBtn" onclick="toggleAlarm()">ARMAR SISTEMA</button>
                <button class="btn green" onclick="testBuzzer()">Testar Buzzer</button>
                <button class="btn blue" onclick="testLED()">Testar LED</button>
                
                <div style="margin-top: 15px;">
                    <h4>Ações Rápidas:</h4>
                    <button class="btn red" onclick="alarmAction('panic')">Alerta de Pânico</button>
                    <button class="btn green" onclick="alarmAction('all_clear')">Tudo Limpo</button>
                </div>
            </div>
            
            <div class="control-panel">
                <h3>Detecção de Movimento</h3>
                <div id="motionStatus" class="alarm-status alarm-disarmed">Status: Carregando...</div>
                
                <button class="btn green" id="motionArmBtn" onclick="toggleMotion()">ARMAR MOVIMENTO</button>
                <button class="btn blue" onclick="testMotionLED()">Testar LED</button>
                
                <div style="margin-top: 15px;">
                    <h4>Fotos Recentes:</h4>
                    <div id="recentPhotos" style="font-size: 0.9em; color: #666;">Carregando...</div>
                    <button class="btn purple" onclick="viewPhotos()">Ver Galeria</button>
                </div>
            </div>
            
            <div class="control-panel">
                <h3>Sistema de Áudio</h3>
                <div id="audioStatus" class="alarm-status alarm-disarmed">Status: Carregando...</div>
                
                <div class="slider-container">
                    <label>Volume: <span id="volumeValue">25</span>%%</label>
                    <input type="range" class="slider" id="volumeSlider" min="0" max="100" value="25" onchange="setVolume()">
                </div>
                
                <button class="btn green" onclick="playSound('startup')">Som Inicialização</button>
                <button class="btn blue" onclick="playSound('success')">Som Sucesso</button>
                <button class="btn purple" onclick="playSound('alert')">Som Alerta</button>
                <button class="btn red" onclick="toggleAudio()">MUDO/SOM</button>
                
                <div style="margin-top: 15px;">
                    <h4>Testes de Áudio:</h4>
                    <button class="btn green" onclick="testAudio()">Teste Completo</button>
                    <button class="btn blue" onclick="playSound('sweep')">Varredura</button>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Sistema Casa Inteligente ESP32-WROVER | Tempo Ativo: UPTIME_PLACEHOLDER minutos</p>
        </div>
    </div>
    
    <script>
        function updateSensors() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    if (data.readings) {
                        document.getElementById('temp').textContent = data.readings.temperature_c + '°C';
                        document.getElementById('humidity').textContent = data.readings.humidity + '%%';
                        document.getElementById('comfort').textContent = data.comfort_level;
                    }
                })
                .catch(error => {
                    console.log('Falha na atualização dos sensores:', error);
                });
        }
        
        function updateRGBStatus() {
            fetch('/api/rgb')
                .then(response => response.json())
                .then(data => {
                    if (data.status) {
                        document.getElementById('rgbStatus').textContent = 'Status: ' + data.current_pattern;
                        document.getElementById('rgbStatus').className = 'alarm-status alarm-disarmed';
                    }
                })
                .catch(error => {
                    document.getElementById('rgbStatus').textContent = 'Status: Offline';
                    document.getElementById('rgbStatus').className = 'alarm-status alarm-armed';
                });
        }
        
        function updateAlarmStatus() {
            fetch('/api/alarm')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('alarmStatus');
                    const armBtn = document.getElementById('armBtn');
                    
                    if (data.armed !== undefined) {
                        if (data.armed) {
                            statusDiv.textContent = 'Status: ARMADO';
                            statusDiv.className = 'alarm-status alarm-armed';
                            armBtn.textContent = 'DESARMAR SISTEMA';
                            armBtn.className = 'btn green';
                        } else {
                            statusDiv.textContent = 'Status: DESARMADO';
                            statusDiv.className = 'alarm-status alarm-disarmed';
                            armBtn.textContent = 'ARMAR SISTEMA';
                            armBtn.className = 'btn red';
                        }
                    }
                })
                .catch(error => {
                    document.getElementById('alarmStatus').textContent = 'Status: Offline';
                });
        }
        
        function updateMotionStatus() {
            fetch('/api/motion')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('motionStatus');
                    const armBtn = document.getElementById('motionArmBtn');
                    
                    if (data.armed !== undefined) {
                        if (data.armed) {
                            statusDiv.textContent = 'Status: ARMADO (' + data.motion_count + ' detecções)';
                            statusDiv.className = 'alarm-status alarm-armed';
                            armBtn.textContent = 'DESARMAR MOVIMENTO';
                            armBtn.className = 'btn green';
                        } else {
                            statusDiv.textContent = 'Status: DESARMADO';
                            statusDiv.className = 'alarm-status alarm-disarmed';
                            armBtn.textContent = 'ARMAR MOVIMENTO';
                            armBtn.className = 'btn red';
                        }
                    }
                    
                    // Update recent photos
                    if (data.storage_info && data.storage_info.photo_count > 0) {
                        document.getElementById('recentPhotos').textContent = data.storage_info.photo_count + ' fotos salvas';
                    } else {
                        document.getElementById('recentPhotos').textContent = 'Nenhuma foto';
                    }
                })
                .catch(error => {
                    document.getElementById('motionStatus').textContent = 'Status: Offline';
                });
        }
        
        function updateAudioStatus() {
            fetch('/api/audio')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('audioStatus');
                    
                    if (data.enabled !== undefined) {
                        if (data.enabled) {
                            statusDiv.textContent = 'Status: ATIVO (Vol: ' + data.volume_percent + '%%)';
                            statusDiv.className = 'alarm-status alarm-disarmed';
                        } else {
                            statusDiv.textContent = 'Status: MUDO';
                            statusDiv.className = 'alarm-status alarm-armed';
                        }
                    }
                })
                .catch(error => {
                    document.getElementById('audioStatus').textContent = 'Status: Offline';
                });
        }
        
        function setRGBColor(r, g, b) {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'color', r: r, g: g, b: b})
            })
            .then(response => response.json())
            .then(data => {
                updateRGBStatus();
                console.log('Cor RGB definida:', r, g, b);
            })
            .catch(error => {
                console.log('Erro ao definir cor RGB:', error);
            });
        }
        
        function setBrightness() {
            const brightness = document.getElementById('brightnessSlider').value;
            document.getElementById('brightnessValue').textContent = brightness;
            
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'brightness', value: brightness})
            })
            .then(() => updateRGBStatus())
            .catch(error => console.log('Erro no brilho:', error));
        }
        
        function rgbPattern(pattern) {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'pattern', pattern: pattern})
            })
            .then(() => updateRGBStatus())
            .catch(error => console.log('Erro no padrão:', error));
        }
        
        function rgbOff() {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'off'})
            })
            .then(() => updateRGBStatus())
            .catch(error => console.log('Erro ao desligar:', error));
        }
        
        function toggleAlarm() {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            })
            .then(() => updateAlarmStatus())
            .catch(error => console.log('Erro no alarme:', error));
        }
        
        function testBuzzer() {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test_buzzer'})
            })
            .then(response => response.json())
            .then(data => console.log('Teste do buzzer realizado'))
            .catch(error => console.log('Erro no teste do buzzer:', error));
        }
        
        function testLED() {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test_led'})
            })
            .then(response => response.json())
            .then(data => console.log('Teste do LED realizado'))
            .catch(error => console.log('Erro no teste do LED:', error));
        }
        
        function alarmAction(action) {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action})
            })
            .then(() => updateAlarmStatus())
            .catch(error => console.log('Erro na ação do alarme:', error));
        }
        
        function toggleMotion() {
            fetch('/api/motion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            })
            .then(() => updateMotionStatus())
            .catch(error => console.log('Erro no alarme:', error));
        }
        
        function testMotionLED() {
            fetch('/api/motion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test_led'})
            })
            .then(response => response.json())
            .then(data => console.log('Teste do LED realizado'))
            .catch(error => console.log('Erro no teste do LED:', error));
        }
        
        function viewPhotos() {
            fetch('/api/photos')
                .then(response => response.json())
                .then(data => {
                    if (data.photos) {
                        document.getElementById('recentPhotos').textContent = 'Fotos recentes: ' + data.photos.join(', ');
                    }
                })
                .catch(error => {
                    console.log('Falha ao carregar fotos:', error);
                });
        }
        
        function setVolume() {
            const volume = document.getElementById('volumeSlider').value;
            document.getElementById('volumeValue').textContent = volume;
            
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'volume', value: volume})
            })
            .then(() => updateAudioStatus())
            .catch(error => console.log('Erro no volume:', error));
        }
        
        function toggleAudio() {
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            })
            .then(() => updateAudioStatus())
            .catch(error => console.log('Erro no áudio:', error));
        }
        
        function testAudio() {
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test'})
            })
            .then(response => response.json())
            .then(data => console.log('Teste de áudio realizado'))
            .catch(error => console.log('Erro no teste de áudio:', error));
        }
        
        function playSound(sound_type) {
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'play', sound: sound_type})
            })
            .then(response => response.json())
            .then(data => console.log('Som reproduzido:', sound_type))
            .catch(error => console.log('Erro ao reproduzir som:', error));
        }
        
        function updateAll() {
            updateSensors();
            updateRGBStatus();
            updateAlarmStatus();
            updateMotionStatus();
            updateAudioStatus();
        }
        
        updateAll();
        setInterval(updateAll, 5000);
    </script>
</body>
</html>"""

STREAM_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Live Camera Stream</title>
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

# =============================================================================
# ROUTE HANDLERS (Simple like main.py)
# =============================================================================

def index(req, resp):
    """Main page handler"""
    global server_status
    server_status['requests_handled'] += 1
    sta_info, ap_info = get_network_info()
    uptime_minutes = int((utime.time() - server_status['start_time']) / 60)
    
    # Use simple string replacement instead of % formatting to avoid conflicts
    content = MAIN_PAGE.replace("STA_INFO_PLACEHOLDER", sta_info)
    content = content.replace("AP_INFO_PLACEHOLDER", ap_info)
    content = content.replace("UPTIME_PLACEHOLDER", str(uptime_minutes))
    
    yield from picoweb.start_response(resp)
    yield from resp.awrite(content)

def stream_page(req, resp):
    """Stream page handler"""
    yield from picoweb.start_response(resp)
    yield from resp.awrite(STREAM_PAGE)

def send_frame():
    """Camera frame generator (same as main.py)"""
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
    """Video stream handler (same as main.py)"""
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
    """Photo capture handler (same as main.py)"""
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
    content = f"""<!DOCTYPE html>
<html>
<head><title>System Status</title>
<style>
    body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
    .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
    .status-card {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
    .nav {{ text-align: center; margin: 20px 0; }}
    .nav a {{ margin: 0 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
</style>
</head>
<body>
    <div class="container">
        <h1>📊 System Status</h1>
        <div class="status-grid">
            <div class="status-card">
                <h3>Uptime</h3>
                <p>{int((utime.time() - server_status['start_time']) / 60)} minutes</p>
            </div>
            <div class="status-card">
                <h3>Free Memory</h3>
                <p>{gc.mem_free()} bytes</p>
            </div>
            <div class="status-card">
                <h3>Requests Handled</h3>
                <p>{server_status['requests_handled']}</p>
            </div>
            <div class="status-card">
                <h3>Modules Status</h3>
                <p>Camera: ✅<br>
                   Sensors: {'✅' if env_sensor else '❌'}<br>
                   Alarm: {'✅' if alarm_system else '❌'}<br>
                   RGB: {'✅' if rgb_strip else '❌'}</p>
            </div>
        </div>
        <div class="nav">
            <a href="/">🏠 Home</a>
            <a href="/stream">📹 Stream</a>
            <a href="/settings">⚙️ Settings</a>
        </div>
    </div>
</body>
</html>"""
    
    yield from picoweb.start_response(resp)
    yield from resp.awrite(content)

# =============================================================================
# API ENDPOINTS (Enhanced with RGB and Alarm controls)
# =============================================================================

def api_sensors(req, resp):
    """Sensors API endpoint"""
    try:
        if env_sensor:
            data = env_sensor.get_environmental_summary()
        else:
            data = {"error": "Environmental sensor not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        try:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite('{"error": "API error"}')
        except:
            pass

def api_rgb(req, resp):
    """RGB strip API endpoint with POST controls"""
    try:
        if req.method == "POST":
            # Handle RGB control commands
            if rgb_strip:
                try:
                    # Read the raw body data
                    content_length = int(req.headers.get(b'Content-Length', 0))
                    if content_length > 0:
                        body = yield from req.reader.readexactly(content_length)
                        data = json.loads(body.decode())
                        action = data.get('action')
                        
                        if action == 'color':
                            r, g, b = data.get('r', 0), data.get('g', 0), data.get('b', 0)
                            rgb_strip.set_all(r, g, b)  # Use correct method name
                        elif action == 'brightness':
                            brightness = int(data.get('value', 50))
                            # For brightness, use a white color scaled by brightness
                            rgb_strip.set_all(brightness, brightness, brightness)
                        elif action == 'pattern':
                            pattern = data.get('pattern', 'solid')
                            if pattern == 'rainbow':
                                rgb_strip.rainbow_cycle()
                            elif pattern == 'breathing':
                                # Implement breathing effect
                                rgb_strip.set_color_name('blue', 100)
                            elif pattern == 'startup':
                                rgb_strip.startup_sequence()
                        elif action == 'off':
                            rgb_strip.clear()
                            
                        yield from picoweb.start_response(resp, content_type="application/json")
                        yield from resp.awrite('{"status": "success"}')
                        return
                except Exception as e:
                    print(f"RGB control error: {e}")
        
        # GET request - return status
        if rgb_strip:
            data = {
                "status": "active",
                "current_pattern": getattr(rgb_strip, 'current_status', 'ready')
            }
        else:
            data = {"error": "RGB strip not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        try:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite('{"error": "API error"}')
        except:
            pass

def api_alarm(req, resp):
    """Alarm system API endpoint with POST controls"""
    try:
        if req.method == "POST":
            # Handle alarm control commands
            if alarm_system:
                try:
                    # Read the raw body data
                    content_length = int(req.headers.get(b'Content-Length', 0))
                    if content_length > 0:
                        body = yield from req.reader.readexactly(content_length)
                        data = json.loads(body.decode())
                        action = data.get('action')
                        
                        if action == 'toggle':
                            if hasattr(alarm_system, 'armed'):
                                if alarm_system.armed:
                                    alarm_system.armed = False
                                else:
                                    alarm_system.armed = True
                        elif action == 'test_buzzer':
                            # Test the passive buzzer
                            if hasattr(alarm_system, 'passive_buzzer'):
                                alarm_system.passive_buzzer.beep(1000, 500)
                        elif action == 'test_led':
                            # Test the status LED
                            if hasattr(alarm_system, 'status_led'):
                                alarm_system.status_led.on()
                                utime.sleep_ms(500)
                                alarm_system.status_led.off()
                        elif action == 'panic':
                            # Trigger alarm sequence
                            if hasattr(alarm_system, 'normal_alarm_sequence'):
                                alarm_system.normal_alarm_sequence()
                        elif action == 'all_clear':
                            # Stop any alarms
                            if hasattr(alarm_system, 'stop_alarm'):
                                alarm_system.stop_alarm()
                                
                        yield from picoweb.start_response(resp, content_type="application/json")
                        yield from resp.awrite('{"status": "success"}')
                        return
                except Exception as e:
                    print(f"Alarm control error: {e}")
        
        # GET request - return status
        if alarm_system:
            data = {
                "armed": getattr(alarm_system, 'armed', False),
                "triggered": getattr(alarm_system, 'alarm_active', False),
                "status": "active"
            }
        else:
            data = {"error": "Alarm system not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        try:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite('{"error": "API error"}')
        except:
            pass

def api_camera(req, resp):
    """Camera API endpoint"""
    try:
        data = {
            "settings": camera_settings,
            "status": "active"
        }
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        yield from picoweb.start_response(resp, status="500")
        yield from resp.awrite('{"error": "API error"}')

def api_system(req, resp):
    """System status API endpoint"""
    try:
        data = {
            "uptime": utime.time() - server_status['start_time'],
            "free_memory": gc.mem_free(),
            "requests_handled": server_status['requests_handled'],
            "errors_count": server_status['errors_count']
        }
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        try:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite('{"error": "API error"}')
        except:
            pass

def api_motion(req, resp):
    """Motion detection API endpoint with POST controls"""
    try:
        if req.method == "POST":
            # Handle motion control commands
            if motion_detector:
                try:
                    # Read the raw body data
                    content_length = int(req.headers.get(b'Content-Length', 0))
                    if content_length > 0:
                        body = yield from req.reader.readexactly(content_length)
                        data = json.loads(body.decode())
                        action = data.get('action')
                        
                        if action == 'toggle':
                            if motion_detector.is_armed:
                                motion_detector.disarm_motion_detection()
                            else:
                                motion_detector.arm_motion_detection()
                        elif action == 'test_led':
                            motion_detector.test_motion_led()
                        elif action == 'arm':
                            motion_detector.arm_motion_detection()
                        elif action == 'disarm':
                            motion_detector.disarm_motion_detection()
                            
                        yield from picoweb.start_response(resp, content_type="application/json")
                        yield from resp.awrite('{"status": "success"}')
                        return
                except Exception as e:
                    print(f"Motion control error: {e}")
        
        # GET request - return status
        if motion_detector:
            data = motion_detector.get_motion_status()
        else:
            data = {"error": "Motion detector not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        try:
            yield from picoweb.start_response(resp, status="500")
            yield from resp.awrite('{"error": "API error"}')
        except:
            pass

def api_audio(req, resp):
    """PWM Audio API endpoint with POST controls"""
    try:
        if req.method == "POST":
            # Handle audio control commands
            if pwm_audio:
                try:
                    # Read the raw body data
                    content_length = int(req.headers.get(b'Content-Length', 0))
                    if content_length > 0:
                        body = yield from req.reader.readexactly(content_length)
                        data = json.loads(body.decode())
                        action = data.get('action')
                        
                        if action == 'toggle':
                            if pwm_audio.is_enabled:
                                pwm_audio.disable_audio()
                            else:
                                pwm_audio.enable_audio()
                        elif action == 'volume':
                            volume = int(data.get('value', 25))
                            pwm_audio.set_volume(volume)
                        elif action == 'play':
                            sound = data.get('sound', 'notification')
                            if sound == 'startup':
                                pwm_audio.play_startup_sound()
                            elif sound == 'success':
                                pwm_audio.play_success_sound()
                            elif sound == 'alert':
                                pwm_audio.play_motion_alert()
                            elif sound == 'alarm':
                                pwm_audio.play_alarm_sound()
                            elif sound == 'error':
                                pwm_audio.play_error_sound()
                            elif sound == 'sweep':
                                pwm_audio.play_sweep()
                            else:
                                pwm_audio.play_notification_beep()
                        elif action == 'test':
                            pwm_audio.test_audio_system()
                            
                        yield from picoweb.start_response(resp, content_type="application/json")
                        yield from resp.awrite('{"status": "success"}')
                        return
                except Exception as e:
                    print(f"Audio control error: {e}")
        
        # GET request - return status
        if pwm_audio:
            data = pwm_audio.get_audio_status()
        else:
            data = {"error": "PWM audio not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        yield from picoweb.start_response(resp, status="500")
        yield from resp.awrite('{"error": "API error"}')

def api_photos(req, resp):
    """Photo gallery API endpoint"""
    try:
        if motion_detector and motion_detector.photo_storage:
            photos = motion_detector.photo_storage.get_photo_list()
            storage_info = motion_detector.photo_storage.get_storage_info()
            data = {
                "photos": photos,
                "storage_info": storage_info
            }
        else:
            data = {"error": "Photo storage not available"}
        
        yield from picoweb.start_response(resp, content_type="application/json")
        yield from resp.awrite(json.dumps(data))
    except OSError:
        pass
    except Exception as e:
        yield from picoweb.start_response(resp, status="500")
        yield from resp.awrite('{"error": "API error"}')

# =============================================================================
# ROUTES LIST (Enhanced with new APIs)
# =============================================================================

ROUTES = [
    ("/", index),
    ("/stream", stream_page),
    ("/video", video_stream),
    ("/settings", settings_handler),
    ("/capture", capture_handler),
    ("/status", status_handler),
    ("/api/sensors", api_sensors),
    ("/api/camera", api_camera),
    ("/api/rgb", api_rgb),
    ("/api/alarm", api_alarm),
    ("/api/system", api_system),
    ("/api/motion", api_motion),
    ("/api/audio", api_audio),
    ("/api/photos", api_photos),
]

def create_web_server():
    """Create and return web server app (like main.py)"""
    print("Creating Smart Home Web Server...")
    app = picoweb.WebApp(__name__, ROUTES)
    return app

def run_server(host="0.0.0.0", port=80, debug=True):
    """Run the web server (simple approach)"""
    print(f"Starting Smart Home Web Server on {host}:{port}")
    app = create_web_server()
    app.run(host=host, port=port, debug=debug) 