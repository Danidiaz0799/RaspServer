# 🍄 RaspServer: Sistema de Control Ambiental para Cultivo de Hongos

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Estado](https://img.shields.io/badge/estado-activo-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-orange)

## 📋 Contenido
- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Sistema Electrónico](#sistema-electrónico)
- [Cultivo de Orellana Rosada](#cultivo-de-orellana-rosada)
- [API](#api)
- [Instalación](#instalación)
- [Soporte](#soporte)

## 📝 Descripción

RaspServer automatiza y monitorea las condiciones ambientales para el cultivo de hongos usando Raspberry Pi tanto para el servidor central como para los nodos de control. El sistema es compatible con cualquier microcontrolador que soporte comunicación MQTT.

**Objetivos:**
- Control ambiental óptimo para cultivos
- Automatización según especies (especializado en orellana rosada)
- Monitoreo en tiempo real con bajo consumo energético

## 🏗️ Arquitectura

```
+-------------------+     +----------------+     
| Raspberry Central |<--->|  Base de Datos |     
|  (Servidor Flask) |     |    (SQLite)    |     
+-------------------+     +----------------+     
          ^
          | MQTT
          v
+---------------------+
|    Broker MQTT      |
|     (Mosquitto)     |
+---------------------+
      ^       ^
     /         \
    /           \
+----------+    +---------------+
| Rasp Pi  |    | Cualquier     |
| (Nodo)   |    | Microcontrol. |
+----------+    +---------------+
```

### Flujo de datos:
1. Sensores conectados a Raspberry Pi o microcontroladores
2. Datos publicados en broker MQTT
3. Servidor central procesa y controla actuadores
4. Sistema optimiza condiciones para orellana rosada

## 🔌 Sistema Electrónico

### 🖥️ Servidor Central (Raspberry Pi)
- **Hardware**: Raspberry Pi 4 (2GB+ RAM)
- **Alimentación**: 5V/3A, adaptador con UPS recomendado
- **Almacenamiento**: microSD 32GB industrial
- **Conectividad**: Ethernet recomendado, WiFi soportado
- **Refrigeración**: Disipador pasivo/activo recomendado

### 📡 Nodos (Raspberry Pi/Microcontroladores)
- **Opciones compatibles**:
  - Raspberry Pi (cualquier modelo)
  - ESP32/ESP8266
  - Arduino + Módulo WiFi/Ethernet
  - Cualquier dispositivo compatible con MQTT

### ⚙️ Circuitos y Electrónica

#### Sensores
- **SHT3X** (I²C)
  - Pines: SDA, SCL, VCC(3.3V), GND
  - Precisión: ±0.2°C / ±2% HR
  - Tiempo respuesta: <8s
  - Consumo: <1mW (promedio)
  
#### Actuadores
1. **Sistema de Iluminación**
  - LED blanco frío, 24W, 6500K
  - MOSFET/Transistor para control PWM
  - Protección contra picos con diodo
  - Optoacoplador recomendado

2. **Ventilador**
  - DC 12V, 200 CFM
  - Control PWM para velocidad variable
  - Protección contra EMI
  - Sensor de tacómetro opcional (feedback)

3. **Humidificador**
  - Ultrasónico, 300ml/h
  - Relé de estado sólido 
  - Protección contra humedad

4. **Motor de Circulación**
  - Brushless 12V, 0.8A
  - Driver dedicado L298N o similar
  - Control PWM de velocidad

#### Esquema de Conexión

```
GPIO Raspberry Pi                Periféricos
+----------------+             +---------------+
| 3.3V      (1) |------------>| VCC SHT3X     |
| SDA (I2C) (3) |<----------->| SDA SHT3X     |
| SCL (I2C) (5) |------------>| SCL SHT3X     |
| GND       (6) |------------>| GND SHT3X     |
| GPIO 17  (11) |--[MOSFET]-->| LED Sistema   |
| GPIO 18  (12) |--[DRIVER]-->| Ventilador    |
| GPIO 27  (13) |----[RELÉ]-->| Humidificador |
| GPIO 22  (15) |--[DRIVER]-->| Motor         |
+----------------+             +---------------+
```

### ⚡ Alimentación y Consumo
- **Servidor**: 5V/3A (15W máx)
- **Nodo**: 5V/2.5A (12.5W) + periféricos
- **Actuadores**: Fuente dedicada 12V/5A
- **Consumo en reposo**: <3W (nodo)
- **Consumo total**: ~60W (sistema completo)

## 🍄 Cultivo de Orellana Rosada

### Parámetros Óptimos (Pleurotus djamor)
| Fase | Temperatura | Humedad | Luz | CO₂ | Duración |
|------|-------------|---------|-----|-----|----------|
| Incubación | 24-28°C | 85-90% | 0h | Alto | 10-14 días |
| Inducción | 22-24°C | 90-95% | 8h | Bajo | 2-3 días |
| Fructificación | 22-26°C | 80-90% | 10h | Bajo | 7-14 días |

### Control Automatizado para Orellana Rosada
- **Temperatura**: Control PID con iluminación y ventilación
- **Humedad**: Ciclos de nebulización programados (4-6 veces/día)
- **Circulación**: Renovación de aire cada 2-3 horas (5 minutos)
- **Iluminación**: Ciclo día/noche según etapa (espectro frío)
- **Registros**: Condiciones óptimas para correlacionar con rendimiento

### Particularidades Electrónicas para P. djamor
- Mayor necesidad de ventilación en fase de fructificación
- Control preciso de humedad (±3%)
- Iluminación suave pero constante durante fructificación
- Sensor adicional de CO₂ recomendado (MH-Z19 opcional)

## 🔌 API

### Endpoints Principales
- `GET /api/clients` - Lista de clientes conectados
- `POST /api/clients` - Registro de nuevo nodo
- `GET /api/clients/{id}/statistics` - Datos históricos
- `PUT /api/clients/{id}/IdealParams` - Configuración de parámetros
- `POST /api/clients/{id}/actuator/toggle_*` - Control de actuadores

### Comunicación MQTT
- `clients/{id}/sensor/sht3x` - Datos de sensores
- `clients/{id}/actuator/*` - Control de actuadores
- `clients/{id}/status/*` - Estado del nodo

## 💻 Instalación

### Componentes Necesarios
- 1x Raspberry Pi 4 (servidor)
- 1x+ Raspberry Pi/ESP32/Arduino (nodos)
- 1x Sensor SHT3X por nodo
- 4x Actuadores por nodo (iluminación, ventilación, humidificación, circulación)
- 1x Fuente 5V/3A para Raspberry
- 1x Fuente 12V/5A para actuadores
- Cables, conectores, relés, transistores

### Preparación de Raspberry Pi

#### 1. Configuración Inicial
```bash
# Instalar Raspberry Pi OS (antes Raspbian)
# 1. Descargar Raspberry Pi Imager desde https://www.raspberrypi.com/software/
# 2. Seleccionar Raspberry Pi OS Lite (64-bit) para mejor rendimiento
# 3. Configurar WiFi, SSH y hostname desde el menú de opciones avanzadas

# Primer arranque - Actualizar sistema
sudo apt update
sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv mosquitto mosquitto-clients i2c-tools
sudo apt install -y libopenjp2-7 libatlas-base-dev  # Dependencias adicionales

# Habilitar I2C para sensores (en servidor y nodos)
sudo raspi-config nonint do_i2c 0
```

#### 2. Configuración del Servidor Central
```bash
# Crear directorio para proyecto
mkdir -p ~/projects
cd ~/projects

# Clonar repositorio
git clone https://github.com/usuario/RaspServer.git
cd RaspServer

# Configurar entorno virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar base de datos
python scripts/init_database.py

# Configurar broker MQTT
sudo cp config/mosquitto.conf /etc/mosquitto/conf.d/raspserver.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

# Configurar servicio systemd para inicio automático
sudo cp config/raspserver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raspserver
sudo systemctl start raspserver

# Verificar estado
sudo systemctl status raspserver
```

#### 3. Configuración de Nodo Cliente (Raspberry Pi)
```bash
# Crear directorio para proyecto
mkdir -p ~/projects
cd ~/projects

# Clonar repositorio
git clone https://github.com/usuario/RaspServer.git
cd RaspServer/node

# Configurar entorno virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements-node.txt

# Configurar parámetros del cliente
nano config/client_config.ini
# Modificar la dirección IP del servidor, ID del cliente y parámetros

# Probar conexión al servidor
python test_connection.py

# Configurar servicio systemd para inicio automático
sudo cp config/raspnode.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raspnode
sudo systemctl start raspnode

# Verificar estado
sudo systemctl status raspnode
```

#### 4. Conexión del Hardware

```bash
# Verificar dispositivos I2C (SHT3X debe aparecer en la dirección 0x44 o 0x45)
i2cdetect -y 1

# Revisar logs para verificar lecturas del sensor
journalctl -u raspnode -f
```

### Verificación de la Instalación

```bash
# En servidor: comprobar que el servidor API está funcionando
curl http://localhost:5000/api/status

# En servidor: comprobar conexiones MQTT
mosquitto_sub -h localhost -t "clients/+/status/heartbeat" -v

# En navegador: abrir la interfaz web
# Abrir http://IP_DEL_SERVIDOR:5000 en el navegador

# Probar API con cliente
curl -X GET "http://IP_DEL_SERVIDOR:5000/api/clients" -H "Content-Type: application/json"
```

### Resolución de Problemas Comunes

1. **Error de conexión MQTT**
   ```bash
   # Verificar que mosquitto está ejecutándose
   sudo systemctl status mosquitto
   
   # Comprobar reglas de firewall
   sudo ufw status
   # Asegurarse que el puerto 1883 está permitido
   ```

2. **Error de sensor SHT3X**
   ```bash
   # Verificar conexiones físicas
   # Comprobar alimentación (3.3V)
   # Verificar si el dispositivo aparece en el bus I2C
   i2cdetect -y 1
   ```

3. **Problemas con la base de datos**
   ```bash
   # Verificar permisos
   ls -la /path/to/database
   
   # Reiniciar base de datos (¡se perderán todos los datos!)
   python scripts/reset_database.py
   ```

### Actualización del Sistema

```bash
# Actualizar desde el repositorio
cd ~/projects/RaspServer
git pull

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicios
sudo systemctl restart raspserver  # En servidor
sudo systemctl restart raspnode    # En nodos
```

## 🆘 Soporte

### Documentación
[https://docs.raspserver.com](https://docs.raspserver.com)

### Contacto
- Email: soporte@raspserver.com
- [GitHub Issues](https://github.com/usuario/RaspServer/issues)

---

<div align="center">
  <p>Desarrollado para cultivos inteligentes de orellana rosada</p>
</div>
