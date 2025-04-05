"""
Utilidades y funciones auxiliares para MSAD
"""
import os
import logging
import threading
import datetime
import time
import atexit
import platform

from msad.config import (
    get_msad_dir,
    get_storage_dir,
    get_log_dir,
    get_config_dir,
    get_database_path,
    ensure_directories,
    IS_WINDOWS
)

# Variables globales para servidor y hilos
_msad_server = None
_backup_thread = None
_running = False

# Configurar logging
def setup_logging():
    """Configurar el sistema de logs"""
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        filename=os.path.join(log_dir, "msad.log"),
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("msad")

# Inicializar logger
logger = setup_logging()

def init():
    """Inicializar el módulo MSAD"""
    logger.info("Inicializando MSAD...")
    logger.info(f"Sistema operativo detectado: {platform.system()}")
    logger.info(f"Usando directorio de almacenamiento: {get_storage_dir()}")
    logger.info(f"Base de datos: {get_database_path()}")
    
    # Verificar si existe la base de datos
    if not os.path.exists(get_database_path()):
        logger.error(f"¡ATENCIÓN! La base de datos no existe en la ruta: {get_database_path()}")
        logger.error("Verifique la ruta correcta de la base de datos")
        print(f"¡ADVERTENCIA! Base de datos no encontrada en: {get_database_path()}")
        print("MSAD continuará, pero los respaldos fallarán hasta que la base de datos exista")
    else:
        logger.info(f"Base de datos encontrada correctamente: {get_database_path()}")
        
        # Crear respaldo inicial
        from msad.core.backup_manager import create_backup
        initial_backup_thread = threading.Thread(target=create_backup)
        initial_backup_thread.daemon = True
        initial_backup_thread.start()
    
    # Verificar si existe el directorio de almacenamiento
    if not os.path.exists(get_storage_dir()):
        logger.warning(f"El directorio {get_storage_dir()} no existe. Creando...")
        try:
            os.makedirs(get_storage_dir(), exist_ok=True)
            logger.info(f"Directorio {get_storage_dir()} creado correctamente")
        except Exception as e:
            logger.error(f"Error al crear directorio {get_storage_dir()}: {str(e)}")
            logger.warning("MSAD continuará funcionando pero puede haber problemas con los respaldos y exportaciones")
    
    # Iniciar hilo para respaldos automáticos
    _start_backup_thread()
    
    logger.info("MSAD inicializado correctamente")
    return True

def _start_backup_thread():
    """Iniciar el hilo de respaldos automáticos"""
    global _backup_thread, _running
    
    _running = True
    _backup_thread = threading.Thread(target=_backup_task)
    _backup_thread.daemon = True
    _backup_thread.start()
    logger.info("Hilo de respaldos automáticos iniciado")

def _backup_task():
    """Función para el hilo de respaldo automático"""
    global _running
    
    from msad.core.backup_manager import create_backup
    
    while _running:
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
            if _running:  # Verificar si aún debe ejecutarse
                create_backup()
            
            # Esperar 24 horas para el siguiente respaldo
            time.sleep(24 * 60 * 60)
        except Exception as e:
            logger.error(f"Error en hilo de respaldo: {str(e)}")
            time.sleep(3600)  # Esperar una hora y reintentar
            
def cleanup():
    """Limpiar recursos al cerrar la aplicación"""
    global _running
    
    logger.info("Limpiando recursos MSAD...")
    
    # Detener hilo de respaldos
    _running = False
    
    # Detener servidor si está activo
    shutdown_msad()
    
    logger.info("MSAD detenido correctamente")

# Registrar función de limpieza para cuando se cierre la aplicación
atexit.register(cleanup)

# Funciones de integración
def init_msad(auto_backup=True, backup_interval_hours=24):
    """
    Inicializar MSAD desde RaspServer
    
    Args:
        auto_backup: Si es True, crea respaldos automáticos
        backup_interval_hours: Intervalo en horas entre respaldos automáticos
        
    Returns:
        dict: Información del estado de la inicialización
    """
    global _msad_server
    
    # Importar aquí para evitar importaciones circulares
    from msad.server.web_server import MSADServer
    
    # Verificar si ya está inicializado
    if _msad_server is not None:
        return {
            "success": True,
            "status": "already_running",
            "message": "MSAD ya está en ejecución"
        }
    
    try:
        # Asegurar que existen los directorios
        ensure_directories()
        
        # Inicializar el servidor MSAD
        _msad_server = MSADServer(start_http=True)
        
        # Crear respaldo inicial si se solicita
        if auto_backup:
            from msad.core.backup_manager import create_backup
            result = create_backup()
            if isinstance(result, dict) and result.get("success"):
                print(f"[MSAD] Respaldo inicial creado: {result.get('backup_path', 'desconocido')}")
            elif result is True:
                print(f"[MSAD] Respaldo inicial creado")
        
        return {
            "success": True,
            "status": "started",
            "message": "MSAD iniciado correctamente",
            "server_info": _msad_server.get_server_status() if _msad_server else {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Error al iniciar MSAD: {str(e)}"
        }

def shutdown_msad():
    """Detener MSAD y liberar recursos"""
    global _msad_server
    
    if _msad_server is not None:
        # Detener el servidor HTTP
        _msad_server.stop_http_server()
        _msad_server = None
        
        print("[MSAD] Servidor MSAD detenido")
        return {"success": True, "message": "MSAD detenido correctamente"}
    
    return {"success": True, "message": "MSAD no estaba en ejecución"}

def get_msad_status():
    """Obtener estado actual de MSAD"""
    global _msad_server
    
    if _msad_server is not None:
        return _msad_server.get_server_status()
    
    return {
        "success": False,
        "error": "MSAD no está inicializado"
    } 