# Sistema de Casa Inteligente ESP32-WROVER

Sistema completo de automação residencial com ESP32-CAM, sensores, LEDs RGB, detecção de movimento e áudio PWM.

## Funcionalidades

- **Câmera**: Streaming ao vivo + captura de fotos
- **Detecção de Movimento**: PIR sensor com captura automática 
- **Monitoramento Ambiental**: Temperatura e umidade (DHT11)
- **LEDs RGB**: 8 LEDs programáveis com efeitos
- **Sistema de Alarme**: 3 tipos de alarme inteligente
- **Áudio PWM**: Notificações sonoras e controle de volume
- **Interface Web**: Controle remoto responsivo
- **WiFi Dual**: Station + Access Point

## Como Usar

### 1. Clonar o Projeto
```bash
git clone https://github.com/seu-usuario/esp32-smart-home.git
cd esp32-smart-home
```

### 2. Flash do Firmware
- Instale o MicroPython no ESP32-CAM
- Use ferramentas como esptool.py ou Thonny IDE
- Flash do firmware: `micropython-esp32cam.bin`



## Documentação Completa

Para detalhes técnicos completos, especificações de hardware, lista de componentes e diagramas de conexão, consulte:

**[📋 Documentação Técnica Completa](docs/report.md)**


## Estrutura do Projeto

```
esp32wroom/
├── main.py              # Sistema principal
├── config.py           # Configurações de pinos
├── modules/
│   ├── motion_detector.py
│   ├── pwm_audio.py
│   ├── web_server.py
│   └── ...
└── lib/                # Bibliotecas MicroPython
```

## Hardware Necessário

- ESP32-CAM AI Thinker
- Sensor PIR HC-SR501
- Sensor DHT11
- Fita LED NeoPixel (8 LEDs)
- Alto-falante 8Ω + Buzzers
- Resistores e jumpers
- Fonte 5V 2A

## Status

 **Sistema Completo e Funcional**
- 8 módulos integrados
- Interface web responsiva  
- Detecção de movimento + fotos
- Sistema de áudio PWM
- Controle total via web

---