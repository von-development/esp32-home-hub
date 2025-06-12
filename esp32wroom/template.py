# ESP32-Optimized Web Templates
# Lightweight, fast-loading templates for ESP32-WROVER Smart Home System
# Based on template2 design but optimized for embedded systems

# =============================================================================
# OPTIMIZED MAIN PAGE TEMPLATE
# =============================================================================

OPTIMIZED_MAIN_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casa Inteligente ESP32</title>
    <style>
        :root {
            --red: #FF4F4F;
            --red-dark: #E03E3E;
            --gray: #F8F9FA;
            --dark: #343A40;
            --white: #FFF;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: var(--gray); color: var(--dark); line-height: 1.5; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 16px; }
        .header { text-align: center; margin-bottom: 24px; padding: 20px 0; }
        .header h1 { font-size: 2rem; font-weight: 700; color: var(--red); margin-bottom: 8px; }
        .header p { color: #666; }
        .card { background: var(--white); border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .nav-card { background: var(--white); border-radius: 8px; padding: 20px; text-decoration: none; color: inherit; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid transparent; transition: border-color 0.2s; }
        .nav-card:hover { border-color: var(--red); }
        .nav-card h3 { font-size: 1.1rem; font-weight: 600; color: var(--red); margin-bottom: 6px; }
        .nav-card p { color: #666; font-size: 0.9rem; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
        .status-item { background: var(--gray); border-radius: 6px; padding: 12px; text-align: center; }
        .status-item h4 { font-size: 0.8rem; font-weight: 600; color: #666; margin-bottom: 4px; text-transform: uppercase; }
        .status-item p { font-weight: 500; }
        .sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
        .sensor-item { background: var(--red); color: var(--white); border-radius: 8px; padding: 16px; text-align: center; }
        .sensor-item h4 { font-size: 0.8rem; margin-bottom: 6px; opacity: 0.9; }
        .sensor-item p { font-size: 1.3rem; font-weight: 700; }
        .control-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .btn { background: var(--red); color: var(--white); border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; margin: 4px; font-size: 0.9rem; }
        .btn:hover { background: var(--red-dark); }
        .btn.green { background: #28a745; }
        .btn.blue { background: #007bff; }
        .color-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 8px 0; }
        .color-btn { width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--white); cursor: pointer; }
        .status-indicator { padding: 12px; border-radius: 6px; text-align: center; font-weight: 600; margin: 8px 0; }
        .status-armed { background: #fff3cd; color: #856404; }
        .status-disarmed { background: #d4edda; color: #155724; }
        .slider { width: 100%; margin: 8px 0; }
        .notification { position: fixed; top: 20px; right: 20px; padding: 12px 20px; border-radius: 6px; color: var(--white); font-weight: 500; z-index: 1000; display: none; }
        .notif-success { background: #28a745; }
        .notif-info { background: #17a2b8; }
        .notif-warning { background: #ffc107; color: var(--dark); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Casa Inteligente ESP32</h1>
            <p>Sistema de Monitoramento e Controle</p>
        </div>
        
        <div class="nav-grid">
            <a href="/stream" class="nav-card">
                <h3>📹 Transmissão ao Vivo</h3>
                <p>Feed da câmera em tempo real</p>
            </a>
            <a href="/capture" class="nav-card">
                <h3>📸 Capturar Foto</h3>
                <p>Tirar foto em alta resolução</p>
            </a>
            <a href="/settings" class="nav-card">
                <h3>⚙️ Configurações</h3>
                <p>Ajustar parâmetros do sistema</p>
            </a>
            <a href="/status" class="nav-card">
                <h3>📊 Status Sistema</h3>
                <p>Monitorar saúde do dispositivo</p>
            </a>
        </div>
        
        <div class="card">
            <h3>🌐 Status da Rede</h3>
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
            <h3>🌡️ Dados Ambientais</h3>
            <div class="sensor-grid">
                <div class="sensor-item">
                    <h4>Temperatura</h4>
                    <p id="temp">--°C</p>
                </div>
                <div class="sensor-item">
                    <h4>Umidade</h4>
                    <p id="humidity">--%</p>
                </div>
                <div class="sensor-item">
                    <h4>Conforto</h4>
                    <p id="comfort">--</p>
                </div>
            </div>
        </div>
        
        <div class="control-grid">
            <div class="card">
                <h3>💡 Controle RGB</h3>
                <div id="rgbStatus" class="status-indicator status-disarmed">Status: Carregando...</div>
                
                <div class="color-grid">
                    <div class="color-btn" style="background:#FF0000" onclick="setColor(255,0,0)" title="Vermelho"></div>
                    <div class="color-btn" style="background:#00FF00" onclick="setColor(0,255,0)" title="Verde"></div>
                    <div class="color-btn" style="background:#0000FF" onclick="setColor(0,0,255)" title="Azul"></div>
                    <div class="color-btn" style="background:#FFFF00" onclick="setColor(255,255,0)" title="Amarelo"></div>
                    <div class="color-btn" style="background:#FF00FF" onclick="setColor(255,0,255)" title="Magenta"></div>
                    <div class="color-btn" style="background:#00FFFF" onclick="setColor(0,255,255)" title="Ciano"></div>
                    <div class="color-btn" style="background:#FFFFFF" onclick="setColor(255,255,255)" title="Branco"></div>
                    <div class="color-btn" style="background:#000000" onclick="setColor(0,0,0)" title="Desligar"></div>
                </div>
                
                <label>Brilho: <span id="brightness">50</span>%</label>
                <input type="range" class="slider" id="brightnessSlider" min="0" max="100" value="50" oninput="setBrightness()">
                
                <div style="margin-top:12px;">
                    <button class="btn" onclick="pattern('rainbow')">🌈 Arco-íris</button>
                    <button class="btn" onclick="pattern('breathing')">💨 Respiração</button>
                    <button class="btn" onclick="rgbOff()">⭕ Desligar</button>
                </div>
            </div>
            
            <div class="card">
                <h3>🚨 Sistema de Alarme</h3>
                <div id="alarmStatus" class="status-indicator status-disarmed">Status: Desarmado</div>
                
                <div style="margin-top:12px;">
                    <button class="btn" id="armBtn" onclick="toggleAlarm()">🔒 Armar Sistema</button>
                    <button class="btn blue" onclick="testBuzzer()">🔊 Testar Buzzer</button>
                </div>
                
                <div style="margin-top:8px;">
                    <button class="btn green" onclick="alarmAction('gentle')">Suave</button>
                    <button class="btn" onclick="alarmAction('normal')">Normal</button>
                    <button class="btn" onclick="alarmAction('urgent')">Urgente</button>
                </div>
            </div>
            
            <div class="card">
                <h3>👁️ Detecção Movimento</h3>
                <div id="motionStatus" class="status-indicator status-disarmed">Status: Desarmado</div>
                
                <div style="margin-top:12px;">
                    <button class="btn" id="motionArmBtn" onclick="toggleMotion()">👁️ Armar Movimento</button>
                    <button class="btn blue" onclick="testMotionLED()">💡 Testar LED</button>
                </div>
                
                <div id="recentPhotos" style="margin-top:8px; padding:8px; background:var(--gray); border-radius:4px; font-size:0.9rem;">
                    Nenhuma foto capturada
                </div>
            </div>
            
            <div class="card">
                <h3>🔊 Sistema de Áudio</h3>
                <div id="audioStatus" class="status-indicator status-disarmed">Status: Ativo</div>
                
                <label>Volume: <span id="volume">50</span>%</label>
                <input type="range" class="slider" id="volumeSlider" min="0" max="100" value="50" oninput="setVolume()">
                
                <div style="margin-top:12px;">
                    <button class="btn" onclick="toggleAudio()">🔇 Mudo/Som</button>
                    <button class="btn blue" onclick="testAudio()">🎵 Testar</button>
                </div>
                
                <div style="margin-top:8px;">
                    <button class="btn green" onclick="playSound('startup')">Inicialização</button>
                    <button class="btn" onclick="playSound('motion')">Movimento</button>
                    <button class="btn" onclick="playSound('alarm')">Alarme</button>
                </div>
            </div>
        </div>
    </div>
    
    <div id="notification" class="notification"></div>
    
    <script>
        // Estado simplificado do sistema
        let state = {
            rgb: {status: 'Pronto', brightness: 50},
            alarm: {armed: false},
            motion: {armed: false, count: 0, photos: 0},
            audio: {active: true, volume: 50}
        };
        
        // Notificações
        function notify(msg, type = 'info') {
            const n = document.getElementById('notification');
            n.textContent = msg;
            n.className = 'notification notif-' + type;
            n.style.display = 'block';
            setTimeout(() => n.style.display = 'none', 3000);
        }
        
        // Controle RGB
        function setColor(r, g, b) {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'color', r: r, g: g, b: b})
            });
            state.rgb.status = `RGB(${r},${g},${b})`;
            updateRGBStatus();
            notify(`Cor: ${r},${g},${b}`, 'success');
        }
        
        function setBrightness() {
            const val = document.getElementById('brightnessSlider').value;
            document.getElementById('brightness').textContent = val;
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'brightness', value: val})
            });
            state.rgb.brightness = val;
            state.rgb.status = `Brilho: ${val}%`;
            updateRGBStatus();
        }
        
        function pattern(p) {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'pattern', pattern: p})
            });
            state.rgb.status = p;
            updateRGBStatus();
            notify(`Padrão: ${p}`, 'success');
        }
        
        function rgbOff() {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'off'})
            });
            state.rgb.status = 'Desligado';
            updateRGBStatus();
            notify('RGB desligado', 'info');
        }
        
        // Sistema de alarme
        function toggleAlarm() {
            state.alarm.armed = !state.alarm.armed;
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            });
            updateAlarmStatus();
            notify(`Alarme ${state.alarm.armed ? 'armado' : 'desarmado'}`, 'warning');
        }
        
        function testBuzzer() {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test_buzzer'})
            });
            notify('Buzzer testado', 'info');
        }
        
        function alarmAction(type) {
            fetch('/api/alarm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: type})
            });
            notify(`Alarme ${type}`, 'warning');
        }
        
        // Detecção de movimento
        function toggleMotion() {
            state.motion.armed = !state.motion.armed;
            fetch('/api/motion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            });
            updateMotionStatus();
            notify(`Movimento ${state.motion.armed ? 'armado' : 'desarmado'}`, 'info');
        }
        
        function testMotionLED() {
            fetch('/api/motion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test_led'})
            });
            notify('LED de movimento testado', 'info');
        }
        
        // Sistema de áudio
        function setVolume() {
            const val = document.getElementById('volumeSlider').value;
            document.getElementById('volume').textContent = val;
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'volume', value: val})
            });
            state.audio.volume = val;
            updateAudioStatus();
        }
        
        function toggleAudio() {
            state.audio.active = !state.audio.active;
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'toggle'})
            });
            updateAudioStatus();
            notify(`Áudio ${state.audio.active ? 'ativo' : 'mudo'}`, 'info');
        }
        
        function testAudio() {
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'test'})
            });
            notify('Áudio testado', 'info');
        }
        
        function playSound(type) {
            fetch('/api/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'play', sound: type})
            });
            notify(`Som: ${type}`, 'info');
        }
        
        // Atualizar status
        function updateRGBStatus() {
            fetch('/api/rgb')
                .then(r => r.json())
                .then(data => {
                    if (data.status) {
                        state.rgb.status = data.current_pattern || 'Pronto';
                        document.getElementById('rgbStatus').textContent = 'Status: ' + state.rgb.status;
                        document.getElementById('rgbStatus').className = 'status-indicator status-disarmed';
                    }
                })
                .catch(() => {
                    document.getElementById('rgbStatus').textContent = 'Status: Offline';
                    document.getElementById('rgbStatus').className = 'status-indicator status-armed';
                });
        }
        
        function updateAlarmStatus() {
            fetch('/api/alarm')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('alarmStatus');
                    const btn = document.getElementById('armBtn');
                    
                    if (data.armed !== undefined) {
                        state.alarm.armed = data.armed;
                        
                        if (data.armed) {
                            status.textContent = 'Status: Armado';
                            status.className = 'status-indicator status-armed';
                            btn.textContent = '🔓 Desarmar Sistema';
                            btn.className = 'btn green';
                        } else {
                            status.textContent = 'Status: Desarmado';
                            status.className = 'status-indicator status-disarmed';
                            btn.textContent = '🔒 Armar Sistema';
                            btn.className = 'btn';
                        }
                    }
                })
                .catch(() => {
                    document.getElementById('alarmStatus').textContent = 'Status: Offline';
                    document.getElementById('alarmStatus').className = 'status-indicator status-armed';
                });
        }
        
        function updateMotionStatus() {
            fetch('/api/motion')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('motionStatus');
                    const btn = document.getElementById('motionArmBtn');
                    const photosDiv = document.getElementById('recentPhotos');
                    
                    if (data.armed !== undefined) {
                        state.motion.armed = data.armed;
                        state.motion.count = data.motion_count || 0;
                        state.motion.photos = data.storage_info ? data.storage_info.photo_count : 0;
                        
                        if (data.armed) {
                            status.textContent = `Status: Armado (${state.motion.count} detecções)`;
                            status.className = 'status-indicator status-armed';
                            btn.textContent = '👁️‍🗨️ Desarmar Movimento';
                            btn.className = 'btn green';
                        } else {
                            status.textContent = 'Status: Desarmado';
                            status.className = 'status-indicator status-disarmed';
                            btn.textContent = '👁️ Armar Movimento';
                            btn.className = 'btn';
                        }
                        
                        // Update photos info
                        if (state.motion.photos > 0) {
                            photosDiv.textContent = `${state.motion.photos} fotos capturadas`;
                        } else {
                            photosDiv.textContent = 'Nenhuma foto capturada';
                        }
                    }
                })
                .catch(() => {
                    document.getElementById('motionStatus').textContent = 'Status: Offline';
                    document.getElementById('motionStatus').className = 'status-indicator status-armed';
                });
        }
        
        function updateAudioStatus() {
            fetch('/api/audio')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('audioStatus');
                    
                    if (data.enabled !== undefined) {
                        state.audio.active = data.enabled;
                        state.audio.volume = data.volume_percent || 50;
                        
                        if (data.enabled) {
                            status.textContent = `Status: Ativo (${state.audio.volume}%)`;
                            status.className = 'status-indicator status-disarmed';
                        } else {
                            status.textContent = 'Status: Mudo';
                            status.className = 'status-indicator status-armed';
                        }
                    }
                })
                .catch(() => {
                    document.getElementById('audioStatus').textContent = 'Status: Offline';
                    document.getElementById('audioStatus').className = 'status-indicator status-armed';
                });
        }
        
        // Atualizar dados dos sensores
        function updateSensors() {
            fetch('/api/sensors')
                .then(r => r.json())
                .then(data => {
                    if (data.readings) {
                        document.getElementById('temp').textContent = data.readings.temperature_c + '°C';
                        document.getElementById('humidity').textContent = data.readings.humidity + '%';
                        document.getElementById('comfort').textContent = data.comfort_level || 'N/A';
                    } else {
                        // Fallback for error cases
                        document.getElementById('temp').textContent = '--°C';
                        document.getElementById('humidity').textContent = '--%';
                        document.getElementById('comfort').textContent = 'Erro';
                    }
                })
                .catch(() => {
                    document.getElementById('temp').textContent = '--°C';
                    document.getElementById('humidity').textContent = '--%';
                    document.getElementById('comfort').textContent = 'Offline';
                });
        }
        
        // Função para atualizar tudo
        function updateAll() {
            updateSensors();
            updateRGBStatus();
            updateAlarmStatus();
            updateMotionStatus();
            updateAudioStatus();
        }
        
        // Inicialização
        updateAll();
        setInterval(updateAll, 5000);
    </script>
</body>
</html>
"""

# =============================================================================
# STREAM PAGE TEMPLATE (Optimized)
# =============================================================================

OPTIMIZED_STREAM_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transmissão - Casa Inteligente</title>
    <style>
        :root { --red: #FF4F4F; --gray: #F8F9FA; --dark: #343A40; --white: #FFF; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: var(--gray); color: var(--dark); }
        .container { max-width: 800px; margin: 0 auto; padding: 16px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: var(--red); }
        .card { background: var(--white); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stream-container { text-align: center; margin-bottom: 20px; }
        #stream { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .controls { text-align: center; }
        .btn { background: var(--red); color: var(--white); border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin: 5px; }
        .btn:hover { opacity: 0.9; }
        .back-link { display: inline-block; margin-top: 15px; color: var(--red); text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📹 Transmissão ao Vivo</h1>
        </div>
        
        <div class="card">
            <div class="stream-container">
                <img id="stream" src="/video" alt="Feed da Câmera">
            </div>
            
            <div class="controls">
                <button class="btn" onclick="refreshStream()">🔄 Atualizar</button>
                <button class="btn" onclick="capturePhoto()">📸 Capturar</button>
            </div>
            
            <a href="/" class="back-link">← Voltar ao Dashboard</a>
        </div>
    </div>
    
    <script>
        function refreshStream() {
            const img = document.getElementById('stream');
            img.src = '/video?' + Date.now();
        }
        
        function capturePhoto() {
            fetch('/capture')
                .then(() => alert('Foto capturada!'))
                .catch(() => alert('Erro ao capturar foto'));
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStream, 30000);
    </script>
</body>
</html>
""" 