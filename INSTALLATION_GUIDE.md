# 🍄 RaspMush: Guía de Instalación Rápida

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)

## 📋 Contenido
- [Requisitos](#requisitos)
- [Instalación Servidor](#instalación-servidor)
- [Configuración MQTT](#configuración-mqtt)
- [Configuración Clientes](#configuración-clientes)
- [Verificación](#verificación)
- [Solución de Problemas](#solución-de-problemas)

## 📝 Requisitos

### Hardware
- Raspberry Pi 4 (2GB+ RAM)
- microSD 32GB Class 10
- Fuente 5V/3A
- Red: Ethernet o WiFi

### Software
- Raspberry Pi OS Lite
- Python 3.7+
- Git, Mosquitto, SQLite

## 💻 Instalación Servidor

### 1. Preparar Sistema Operativo
```bash
# Actualizar e instalar dependencias
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv mosquitto sqlite3 avahi-daemon

# Habilitar servicios
sudo systemctl enable --now mosquitto avahi-daemon
```

### 2. Instalar RaspMush
```bash
# Clonar y configurar
git clone https://github.com/usuario/RaspMush.git ~/RaspMush
cd ~/RaspMush
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Inicializar base de datos
python scripts/init_db.py

# Configurar hostname
sudo hostnamectl set-hostname raspmush
```

### 3. Configurar Servicio
```bash
sudo cp config/raspmush.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now raspmush
```

## 📡 Configuración MQTT

### Configurar Broker MQTT
```bash
# Crear configuración personalizada
echo -e "listener 1883\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/raspmush.conf
sudo systemctl restart mosquitto

# Verificar (en terminal separada)
mosquitto_sub -h localhost -t "test" &
mosquitto_pub -h localhost -t "test" -m "Prueba"
```

## 🌐 Configuración Red

El sistema usa mDNS para acceso con nombre estable `raspmush.local`.

```bash
# Verificar funcionamiento
ping raspmush.local

# Accesos:
# - API: http://raspmush.local:5000
# - MQTT: raspmush.local:1883
```

## 🔌 Configuración Clientes

### Nodo Raspberry Pi
```bash
# Instalar dependencias
sudo apt install -y python3-pip
pip3 install paho-mqtt adafruit-circuitpython-sht31d

# Descargar cliente
wget -O ~/raspmush-client.py https://github.com/usuario/RaspMush/raw/main/clients/raspmush-client.py

# Configurar y ejecutar
nano ~/raspmush-client.py  # Editar parámetros
python3 ~/raspmush-client.py
```

### Nodo ESP32/ESP8266
1. Instalar librerías en Arduino IDE:
   - PubSubClient
   - ArduinoJson
   - Adafruit SHT31

2. Descargar sketch desde `/clients/esp32_client` en repositorio
3. Configurar WiFi y MQTT
4. Cargar en el dispositivo

## ✅ Verificación

### Verificar Funcionamiento
```bash
# Estado del servidor
sudo systemctl status raspmush

# Verificar API
curl http://localhost:5000/api/status

# Monitorear mensajes MQTT
mosquitto_sub -h localhost -t "cultivos/#" -v
```

## 🔧 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| No se conecta a MQTT | `sudo systemctl restart mosquitto` |
| No resuelve raspmush.local | `sudo systemctl restart avahi-daemon` |
| Error en servidor | Revisar logs: `sudo journalctl -u raspmush -f` |
| Falta espacio | Limpiar logs: `sudo journalctl --vacuum-time=2d` |

### Comandos Útiles
```bash
# Reiniciar servicios
sudo systemctl restart raspmush
sudo systemctl restart mosquitto

# Obtener IP si mDNS falla
hostname -I

# Resetear base de datos (borra todos los datos)
python scripts/reset_db.py
```

## 🔄 Actualización

Para actualizar el sistema:
```bash
cd ~/RaspMush
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart raspmush
```

---

<div align="center">
  <p>Para información técnica detallada, consulte el archivo <a href="README.md">README.md</a></p>
</div> 