# ESP32 Smart Home Hub - Work in Progress

Sistema de automação residencial usando ESP32-WROVER com câmera, sensores e LEDs RGB.

## Hardware

- **ESP32-WROVER** com câmera OV2640 integrada
- **DHT11** - Sensor temperatura/umidade (Pino 15)
- **8-RGB-LED** - Strip LEDs addressáveis (Pino 2)

## Conexões

### DHT11
```
VCC  → 3.3V
DATA → Pino 15
GND  → GND
```

### 8-RGB-LED
```
VCC → 3.3V
DIN → Pino 2  
GND → GND
```

## Implementado

### Câmera
- Streaming JPEG na rota `/`
- Captura de fotos via web
- Interface responsiva

### Sensores
- Leitura DHT11 (Temperatura, Humidade..)


### LEDs RGB
- 8 LEDs controlados individualmente
- Padrões visuais para status
- Animações (arco-íris, gradientes)

### Conectividade
- WiFi dual (STA + AP)
- Servidor web com picoweb
- Interface multi-página

## Estrutura

```
esp32wroom/
├── main.py                    
├── modules/
│   ├── environmental_sensor.py 
│   └── rgb_strip.py          
└── lib/picoweb/             
```


## Ainda Falta Fazer

### Fase 3 - Segurança
- [ ] Sensor PIR de movimento
- [ ] Sistema de alarme
- [ ] Notificações de movimento

### Fase 4 - Interface Local  
- [ ] Display LCD 16x2
- [ ] Teclado matricial 4x4
- [ ] Menu de configuração local
- [ ] Controle sem web



## Tecnologias

- MicroPython
- Picoweb (servidor web)
- NeoPixel (LEDs)
- Socket (rede)

## Status

**Funcional**: Câmera + DHT11 + LEDs RGB + Interface web
**Próximo**: Sensores PIR para detecção de movimento

---
