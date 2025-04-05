"""
Funciones de respaldo y mantenimiento de la base de datos
"""
import os
import sqlite3
import datetime
import glob

from msad.config import (
    get_storage_dir,
    get_database_path,
    IS_WINDOWS,
    get_backup_retention
)
from msad.core.system_utils import logger

def create_backup():
    """Crear respaldo de la base de datos SQLite"""
    storage_dir = get_storage_dir()
    db_path = get_database_path()
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        day_of_week = datetime.datetime.now().weekday()  # 0-6 (lunes-domingo)
        day_of_month = datetime.datetime.now().day  # 1-31
        
        # Respaldo diario
        backup_path = os.path.join(storage_dir, "backups", "daily", f"sensor_data_{timestamp}.db")
        
        if os.path.exists(db_path):
            # Usar SQLite para hacer backup atómico
            conn = sqlite3.connect(db_path)
            with conn:
                # Guardar el estado de la base de datos
                conn.execute(f"VACUUM INTO '{backup_path}'")
            conn.close()
            
            logger.info(f"Respaldo diario creado: {backup_path}")
            
            # Respaldo semanal (domingo)
            if day_of_week == 6:
                weekly_path = os.path.join(storage_dir, "backups", "weekly", f"sensor_data_{timestamp}.db")
                if IS_WINDOWS:
                    # Usar copy en Windows
                    os.system(f'copy "{backup_path}" "{weekly_path}"')
                else:
                    # Usar cp en Linux/macOS
                    os.system(f'cp "{backup_path}" "{weekly_path}"')
                logger.info(f"Respaldo semanal creado: {weekly_path}")
            
            # Respaldo mensual (día 1)
            if day_of_month == 1:
                monthly_path = os.path.join(storage_dir, "backups", "monthly", f"sensor_data_{timestamp}.db")
                if IS_WINDOWS:
                    # Usar copy en Windows
                    os.system(f'copy "{backup_path}" "{monthly_path}"')
                else:
                    # Usar cp en Linux/macOS
                    os.system(f'cp "{backup_path}" "{monthly_path}"')
                logger.info(f"Respaldo mensual creado: {monthly_path}")
                
            # Limpieza: mantener últimos 7 respaldos diarios
            cleanup_old_backups()
            
            return {
                "success": True,
                "backup_path": backup_path,
                "timestamp": timestamp
            }
        else:
            logger.error(f"Base de datos no encontrada: {db_path}")
            print(f"Error: Base de datos no encontrada en: {db_path}")
            return {
                "success": False,
                "error": f"Base de datos no encontrada: {db_path}"
            }
    except Exception as e:
        logger.error(f"Error al crear respaldo: {str(e)}")
        print(f"Error al crear respaldo: {str(e)}")
        return {
            "success": False,
            "error": f"Error al crear respaldo: {str(e)}"
        }

def cleanup_old_backups():
    """Limpiar respaldos antiguos"""
    storage_dir = get_storage_dir()
    
    try:
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
        
        # Obtener configuración de retención
        daily_retention = get_backup_retention("daily")
        weekly_retention = get_backup_retention("weekly")
        monthly_retention = get_backup_retention("monthly")
                    
        # Mantener últimos respaldos diarios
        keep_newest_n(os.path.join(storage_dir, "backups", "daily"), "*.db", daily_retention)
        
        # Mantener últimos respaldos semanales
        keep_newest_n(os.path.join(storage_dir, "backups", "weekly"), "*.db", weekly_retention)
        
        # Mantener últimos respaldos mensuales
        keep_newest_n(os.path.join(storage_dir, "backups", "monthly"), "*.db", monthly_retention)
        
        logger.info("Limpieza de respaldos antiguos completada")
        return True
    except Exception as e:
        logger.error(f"Error al limpiar respaldos antiguos: {str(e)}")
        return False 