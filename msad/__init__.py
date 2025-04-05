# MSAD - Microservicio de Almacenamiento Distribuido
# Este archivo mantiene la carpeta como un módulo Python
# La funcionalidad principal se encuentra en run_msad.py

__version__ = '1.0.0'

import os
import sqlite3
import logging
import datetime
import threading
import time
import atexit
import platform
from pathlib import Path

# Detectar sistema operativo
IS_WINDOWS = platform.system() == "Windows"

# Configuración
MSAD_DIR = os.path.dirname(os.path.abspath(__file__))
if IS_WINDOWS:
    # Ruta para Windows - Usar la ruta actual adaptada a Windows
    STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "msad")
else:
    # Ruta para Linux/Raspberry Pi
    STORAGE_DIR = "/mnt/storage/msad"

LOG_DIR = os.path.join(MSAD_DIR, "logs")
CONFIG_DIR = os.path.join(MSAD_DIR, "config")

# Detectar ruta de la base de datos - Adaptada a partir de database.py
if IS_WINDOWS:
    # En Windows, usar la misma ubicación pero adaptada a la estructura de Windows
    # Reemplazar la ruta Linux con la ruta Windows equivalente
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sensor_data.db")
else:
    # En Linux, usar la ruta exacta que aparece en database.py
    DB_PATH = "/home/stevpi/Desktop/raspServer/sensor_data.db"

# Asegurar que los directorios existan
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Asegurar que los directorios de almacenamiento existan
try:
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "daily"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "weekly"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "backups", "monthly"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "exports", "csv"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "exports", "json"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "data", "clients"), exist_ok=True)
except Exception as e:
    # Si falla la creación de directorios, registrar el error pero no detener la aplicación
    print(f"Error al crear directorios de almacenamiento: {str(e)}")
    print(f"Algunas funciones de MSAD pueden no trabajar correctamente")

# Configurar logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "msad.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("msad")

def create_backup():
    """Crear respaldo de la base de datos SQLite"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        day_of_week = datetime.datetime.now().weekday()  # 0-6 (lunes-domingo)
        day_of_month = datetime.datetime.now().day  # 1-31
        
        # Respaldo diario
        backup_path = os.path.join(STORAGE_DIR, "backups", "daily", f"sensor_data_{timestamp}.db")
        
        if os.path.exists(DB_PATH):
            # Usar SQLite para hacer backup atómico
            conn = sqlite3.connect(DB_PATH)
            with conn:
                # Guardar el estado de la base de datos
                conn.execute(f"VACUUM INTO '{backup_path}'")
            conn.close()
            
            logger.info(f"Respaldo diario creado: {backup_path}")
            
            # Respaldo semanal (domingo)
            if day_of_week == 6:
                weekly_path = os.path.join(STORAGE_DIR, "backups", "weekly", f"sensor_data_{timestamp}.db")
                if IS_WINDOWS:
                    # Usar copy en Windows
                    os.system(f'copy "{backup_path}" "{weekly_path}"')
                else:
                    # Usar cp en Linux/macOS
                    os.system(f'cp "{backup_path}" "{weekly_path}"')
                logger.info(f"Respaldo semanal creado: {weekly_path}")
            
            # Respaldo mensual (día 1)
            if day_of_month == 1:
                monthly_path = os.path.join(STORAGE_DIR, "backups", "monthly", f"sensor_data_{timestamp}.db")
                if IS_WINDOWS:
                    # Usar copy en Windows
                    os.system(f'copy "{backup_path}" "{monthly_path}"')
                else:
                    # Usar cp en Linux/macOS
                    os.system(f'cp "{backup_path}" "{monthly_path}"')
                logger.info(f"Respaldo mensual creado: {monthly_path}")
                
            # Limpieza: mantener últimos 7 respaldos diarios
            cleanup_old_backups()
            
            return True
        else:
            logger.error(f"Base de datos no encontrada: {DB_PATH}")
            print(f"Error: Base de datos no encontrada en: {DB_PATH}")
            return False
    except Exception as e:
        logger.error(f"Error al crear respaldo: {str(e)}")
        print(f"Error al crear respaldo: {str(e)}")
        return False

def cleanup_old_backups():
    """Limpiar respaldos antiguos"""
    try:
        import glob
        import os
        
        # Función para limpiar archivos antiguos
        def keep_newest_n(directory, pattern, n):
            if not os.path.exists(directory):
                logger.warning(f"Directorio no encontrado: {directory}")
                return
                
            files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime, reverse=True)
            for file in files[n:]:
                try:
                    os.remove(file)
                    logger.info(f"Archivo antiguo eliminado: {file}")
                except Exception as e:
                    logger.error(f"Error al eliminar archivo: {file}, {str(e)}")
                    
        # Mantener últimos 7 respaldos diarios
        keep_newest_n(os.path.join(STORAGE_DIR, "backups", "daily"), "*.db", 7)
        
        # Mantener últimos 4 respaldos semanales
        keep_newest_n(os.path.join(STORAGE_DIR, "backups", "weekly"), "*.db", 4)
        
        # Mantener últimos 3 respaldos mensuales
        keep_newest_n(os.path.join(STORAGE_DIR, "backups", "monthly"), "*.db", 3)
        
        logger.info("Limpieza de respaldos antiguos completada")
        return True
    except Exception as e:
        logger.error(f"Error al limpiar respaldos antiguos: {str(e)}")
        return False

def backup_thread_function():
    """Función para el hilo de respaldo automático"""
    while True:
        try:
            # Esperar hasta medianoche para el primer respaldo
            now = datetime.datetime.now()
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run = next_run + datetime.timedelta(days=1)
            
            # Calcular segundos hasta la próxima ejecución
            seconds_until_next_run = (next_run - now).total_seconds()
            logger.info(f"Próximo respaldo programado en {seconds_until_next_run/3600:.1f} horas")
            
            # Esperar hasta la hora programada
            time.sleep(seconds_until_next_run)
            
            # Ejecutar respaldo
            create_backup()
            
            # Esperar 24 horas para el siguiente respaldo
            time.sleep(24 * 60 * 60)
        except Exception as e:
            logger.error(f"Error en hilo de respaldo: {str(e)}")
            time.sleep(3600)  # Esperar una hora y reintentar

def init():
    """Inicializar el módulo MSAD"""
    logger.info("Inicializando MSAD...")
    logger.info(f"Sistema operativo detectado: {platform.system()}")
    logger.info(f"Usando directorio de almacenamiento: {STORAGE_DIR}")
    logger.info(f"Base de datos: {DB_PATH}")
    
    # Verificar si existe la base de datos
    if not os.path.exists(DB_PATH):
        logger.error(f"¡ATENCIÓN! La base de datos no existe en la ruta: {DB_PATH}")
        logger.error("Verifique la ruta correcta de la base de datos y actualice la variable DB_PATH")
        print(f"¡ADVERTENCIA! Base de datos no encontrada en: {DB_PATH}")
        print("MSAD continuará, pero los respaldos fallarán hasta que la base de datos exista")
    else:
        logger.info(f"Base de datos encontrada correctamente: {DB_PATH}")
        
        # Crear respaldo inicial
        initial_backup_thread = threading.Thread(target=create_backup)
        initial_backup_thread.daemon = True
        initial_backup_thread.start()
    
    # Verificar si existe el directorio de almacenamiento
    if not os.path.exists(STORAGE_DIR):
        logger.warning(f"El directorio {STORAGE_DIR} no existe. Creando...")
        try:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            logger.info(f"Directorio {STORAGE_DIR} creado correctamente")
        except Exception as e:
            logger.error(f"Error al crear directorio {STORAGE_DIR}: {str(e)}")
            logger.warning("MSAD continuará funcionando pero puede haber problemas con los respaldos y exportaciones")
    
    # Iniciar hilo para respaldos automáticos
    backup_thread = threading.Thread(target=backup_thread_function)
    backup_thread.daemon = True
    backup_thread.start()
    
    logger.info("MSAD inicializado correctamente")
    return True

def cleanup():
    """Limpiar recursos al cerrar la aplicación"""
    logger.info("Limpiando recursos MSAD...")
    # No se necesita una limpieza especial, solo registrar
    logger.info("MSAD detenido correctamente")

# Registrar función de limpieza para cuando se cierre la aplicación
atexit.register(cleanup) 