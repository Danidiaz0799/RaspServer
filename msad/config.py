"""
Configuración compartida para RaspServer y MSAD
Este archivo permite centralizar las rutas y parámetros
"""
import os
import platform

# Detectar sistema operativo
IS_WINDOWS = platform.system() == "Windows"

# Configuración de rutas
if IS_WINDOWS:
    # Rutas para Windows
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(BASE_DIR, "sensor_data.db")
    STORAGE_DIR = os.path.join(BASE_DIR, "storage", "msad")
else:
    # Rutas para Raspberry Pi
    BASE_DIR = "/home/stevpi/Desktop/raspServer"
    DATABASE_PATH = os.path.join(BASE_DIR, "sensor_data.db")
    STORAGE_DIR = "/mnt/storage/msad"

# Configuración del servidor HTTP
HTTP_PORT = 8080

# Configuración de respaldos
BACKUP_RETENTION = {
    "daily": 7,    # Número de respaldos diarios a mantener
    "weekly": 4,   # Número de respaldos semanales a mantener
    "monthly": 6   # Número de respaldos mensuales a mantener
}

# Crear directorios necesarios
def ensure_directories():
    """Crear directorios necesarios si no existen"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "daily"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "weekly"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "monthly"), exist_ok=True) 