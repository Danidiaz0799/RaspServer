"""
Módulo de integración para RaspServer
Este archivo facilita la integración del MSAD con la aplicación principal
"""
import threading
import time
import datetime
import atexit

from msad.server import MSADServer
from msad.config import ensure_directories

# Variable global para el servidor MSAD
_msad_server = None
_backup_thread = None
_running = False

def init_msad(auto_backup=True, backup_interval_hours=24):
    """
    Inicializar MSAD desde RaspServer
    
    Args:
        auto_backup: Si es True, crea respaldos automáticos
        backup_interval_hours: Intervalo en horas entre respaldos automáticos
        
    Returns:
        dict: Información del estado de la inicialización
    """
    global _msad_server, _backup_thread, _running
    
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
        
        # Registro para limpieza al salir
        atexit.register(shutdown_msad)
        
        # Iniciar hilo de respaldos automáticos si se solicita
        if auto_backup:
            _running = True
            _backup_thread = threading.Thread(
                target=_backup_task, 
                args=(backup_interval_hours,)
            )
            _backup_thread.daemon = True
            _backup_thread.start()
        
        # Crear respaldo inicial
        if auto_backup:
            result = _msad_server.create_backup()
            if result["success"]:
                print(f"[MSAD] Respaldo inicial creado: {result['backup_path']}")
        
        return {
            "success": True,
            "status": "started",
            "message": "MSAD iniciado correctamente",
            "server_info": _msad_server.get_server_status()
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Error al iniciar MSAD: {str(e)}"
        }

def shutdown_msad():
    """Detener MSAD y liberar recursos"""
    global _msad_server, _backup_thread, _running
    
    if _msad_server is not None:
        # Detener el hilo de respaldos automáticos
        _running = False
        if _backup_thread is not None:
            _backup_thread.join(timeout=1)
        
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

def create_backup():
    """Crear un respaldo bajo demanda"""
    global _msad_server
    
    if _msad_server is not None:
        return _msad_server.create_backup()
    
    return {
        "success": False,
        "error": "MSAD no está inicializado"
    }

def _backup_task(interval_hours):
    """Tarea en segundo plano para crear respaldos automáticos"""
    global _msad_server, _running
    
    last_backup = datetime.datetime.now()
    
    while _running:
        # Verificar si es hora de hacer un respaldo
        now = datetime.datetime.now()
        elapsed = now - last_backup
        
        if elapsed.total_seconds() >= interval_hours * 3600:
            # Crear respaldo
            if _msad_server is not None:
                result = _msad_server.create_backup()
                if result["success"]:
                    print(f"[MSAD] Respaldo automático creado: {result['backup_path']}")
                last_backup = now
        
        # Esperar un poco para no consumir CPU
        time.sleep(60)  # Verificar cada minuto 