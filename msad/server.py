#!/usr/bin/env python3
"""
MSAD - Servidor de respaldos y acceso HTTP
Módulo principal con funcionalidades de backup y servidor
"""
import os
import sqlite3
import datetime
import http.server
import socketserver
import threading
import sys
import shutil
import json
from queue import Queue
import time

# Importar configuración compartida
from msad.config import (
    DATABASE_PATH, 
    STORAGE_DIR, 
    HTTP_PORT,
    BACKUP_RETENTION,
    ensure_directories
)

class MSADServer:
    """Clase principal del servidor MSAD"""
    
    def __init__(self, start_http=True):
        """Inicializar el servidor MSAD"""
        # Asegurar que existen los directorios
        ensure_directories()
        
        # Variables de servidor
        self.server_thread = None
        self.httpd = None
        self.running = False
        
        # Cola de mensajes para comunicación entre hilos
        self.message_queue = Queue()
        
        # Iniciar servidor HTTP si se solicita
        if start_http:
            self.start_http_server()
    
    def start_http_server(self):
        """Iniciar el servidor HTTP"""
        def run():
            # Copiar el archivo index.html al directorio de almacenamiento
            index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
            if os.path.exists(index_path):
                shutil.copy2(index_path, os.path.join(STORAGE_DIR, "index.html"))
            
            os.chdir(STORAGE_DIR)
            handler = http.server.SimpleHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", HTTP_PORT), handler)
            
            # Obtener la IP local para mostrarla
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            print(f"\n[MSAD] Servidor HTTP iniciado en http://{ip}:{HTTP_PORT}")
            self.running = True
            
            # Añadir mensaje a la cola
            self.message_queue.put({
                "type": "server_started",
                "url": f"http://{ip}:{HTTP_PORT}"
            })
            
            self.httpd.serve_forever()
            
        self.server_thread = threading.Thread(target=run)
        self.server_thread.daemon = True
        self.server_thread.start()
        return True
    
    def stop_http_server(self):
        """Detener el servidor HTTP"""
        if self.httpd and self.running:
            self.httpd.shutdown()
            self.running = False
            self.message_queue.put({"type": "server_stopped"})
            print("[MSAD] Servidor HTTP detenido")
            return True
        return False
    
    def create_backup(self, notify=True):
        """Crear respaldo de la base de datos"""
        try:
            # Asegurar que existen los directorios
            ensure_directories()
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(STORAGE_DIR, "backups", "daily", f"sensor_data_{timestamp}.db")
            
            if os.path.exists(DATABASE_PATH):
                # Crear respaldo con SQLite
                conn = sqlite3.connect(DATABASE_PATH)
                with conn:
                    conn.execute(f"VACUUM INTO '{backup_path}'")
                conn.close()
                
                # Crear respaldos semanales y mensuales si es necesario
                now = datetime.datetime.now()
                
                # Verificar si es domingo (día 6)
                if now.weekday() == 6:
                    weekly_path = os.path.join(STORAGE_DIR, "backups", "weekly", f"sensor_data_{timestamp}.db")
                    shutil.copy2(backup_path, weekly_path)
                    print(f"[MSAD] Respaldo semanal creado: {weekly_path}")
                
                # Verificar si es día 1 del mes
                if now.day == 1:
                    monthly_path = os.path.join(STORAGE_DIR, "backups", "monthly", f"sensor_data_{timestamp}.db")
                    shutil.copy2(backup_path, monthly_path)
                    print(f"[MSAD] Respaldo mensual creado: {monthly_path}")
                
                # Limpiar respaldos antiguos
                self._cleanup_old_backups()
                
                # Notificar del respaldo creado
                if notify:
                    self.message_queue.put({
                        "type": "backup_created",
                        "path": backup_path,
                        "timestamp": timestamp
                    })
                    
                return {
                    "success": True,
                    "backup_path": backup_path,
                    "timestamp": timestamp
                }
            else:
                error_msg = f"Error: Base de datos no encontrada: {DATABASE_PATH}"
                print(f"[MSAD] {error_msg}")
                
                if notify:
                    self.message_queue.put({
                        "type": "backup_error",
                        "error": error_msg
                    })
                
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            error_msg = f"Error al crear respaldo: {str(e)}"
            print(f"[MSAD] {error_msg}")
            
            if notify:
                self.message_queue.put({
                    "type": "backup_error",
                    "error": error_msg
                })
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def _cleanup_old_backups(self):
        """Limpiar respaldos antiguos basado en la política de retención"""
        try:
            # Limpiar respaldos diarios
            self._cleanup_backup_type("daily", BACKUP_RETENTION["daily"])
            
            # Limpiar respaldos semanales
            self._cleanup_backup_type("weekly", BACKUP_RETENTION["weekly"])
            
            # Limpiar respaldos mensuales
            self._cleanup_backup_type("monthly", BACKUP_RETENTION["monthly"])
            
        except Exception as e:
            print(f"[MSAD] Error al limpiar respaldos antiguos: {str(e)}")
    
    def _cleanup_backup_type(self, backup_type, keep_count):
        """Limpiar un tipo específico de respaldos"""
        backup_dir = os.path.join(STORAGE_DIR, "backups", backup_type)
        if not os.path.exists(backup_dir):
            return
            
        # Obtener lista de archivos ordenados por fecha (el más reciente primero)
        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.db')],
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
            reverse=True
        )
        
        # Eliminar archivos antiguos
        if len(files) > keep_count:
            for old_file in files[keep_count:]:
                try:
                    os.remove(os.path.join(backup_dir, old_file))
                    print(f"[MSAD] Respaldo antiguo eliminado: {old_file}")
                except Exception as e:
                    print(f"[MSAD] Error al eliminar respaldo: {old_file} - {str(e)}")
    
    def get_server_status(self):
        """Obtener información del estado del servidor"""
        try:
            # Obtener la IP local
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # Contar respaldos
            daily_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "daily")) 
                              if f.endswith(".db")])
            weekly_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "weekly")) 
                               if f.endswith(".db")])
            monthly_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "monthly")) 
                                if f.endswith(".db")])
            
            # Calcular espacio utilizado
            import platform
            if platform.system() == "Windows":
                # Windows: usar os.path.getsize
                daily_size = sum(os.path.getsize(os.path.join(STORAGE_DIR, "backups", "daily", f)) 
                                for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "daily")) 
                                if f.endswith(".db"))
                weekly_size = sum(os.path.getsize(os.path.join(STORAGE_DIR, "backups", "weekly", f)) 
                                 for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "weekly")) 
                                 if f.endswith(".db"))
                monthly_size = sum(os.path.getsize(os.path.join(STORAGE_DIR, "backups", "monthly", f)) 
                                  for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "monthly")) 
                                  if f.endswith(".db"))
            else:
                # Linux: usar comando du
                daily_size = os.popen(f"du -s {os.path.join(STORAGE_DIR, 'backups', 'daily')}").read().split()[0]
                weekly_size = os.popen(f"du -s {os.path.join(STORAGE_DIR, 'backups', 'weekly')}").read().split()[0]
                monthly_size = os.popen(f"du -s {os.path.join(STORAGE_DIR, 'backups', 'monthly')}").read().split()[0]
            
            return {
                "success": True,
                "server": {
                    "active": self.running,
                    "url": f"http://{ip}:{HTTP_PORT}" if self.running else None,
                    "port": HTTP_PORT
                },
                "storage": {
                    "path": STORAGE_DIR,
                    "database": DATABASE_PATH
                },
                "backups": {
                    "daily": {
                        "count": daily_count,
                        "size": daily_size
                    },
                    "weekly": {
                        "count": weekly_count,
                        "size": weekly_size
                    },
                    "monthly": {
                        "count": monthly_count,
                        "size": monthly_size
                    }
                },
                "retention_policy": BACKUP_RETENTION
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_interactive(self):
        """Ejecutar MSAD con menú interactivo"""
        try:
            print("======================================")
            print("      MSAD - Sistema de Respaldos     ")
            print("======================================")
            import platform
            print(f"Sistema: {platform.system()}")
            print(f"Base de datos: {DATABASE_PATH}")
            print(f"Almacenamiento: {STORAGE_DIR}")
            
            # Verificar si existe la base de datos
            if not os.path.exists(DATABASE_PATH):
                print("\n⚠️  ADVERTENCIA: Base de datos no encontrada.")
                print("   Primero debes ejecutar app.py para crear la base de datos.")
                print("   ¿Deseas continuar de todos modos? (s/n)")
                choice = input("   > ")
                if choice.lower() != 's':
                    print("Saliendo...")
                    return
            
            # Iniciar servidor HTTP si no está iniciado
            if not self.running:
                self.start_http_server()
            
            # Menú principal
            while True:
                print("\n==== MSAD - Menú Principal ====")
                print("1. Crear respaldo manual")
                print("2. Ver información del servidor")
                print("3. Salir")
                
                choice = input("\nSelecciona una opción (1-3): ")
                
                if choice == "1":
                    result = self.create_backup()
                    if result["success"]:
                        print(f"✓ Respaldo creado: {result['backup_path']}")
                    else:
                        print(f"✗ {result['error']}")
                        
                elif choice == "2":
                    status = self.get_server_status()
                    
                    if status["success"]:
                        print("\nInformación del servidor:")
                        print(f"- Estado: {'Activo' if status['server']['active'] else 'Inactivo'}")
                        print(f"- URL de acceso: {status['server']['url']}")
                        print(f"- Directorio de datos: {status['storage']['path']}")
                        print(f"- Base de datos: {status['storage']['database']}")
                        print(f"- Respaldos: {status['backups']['daily']['count']} diarios, "
                              f"{status['backups']['weekly']['count']} semanales, "
                              f"{status['backups']['monthly']['count']} mensuales")
                    else:
                        print(f"✗ Error al obtener información: {status['error']}")
                        
                elif choice == "3":
                    print("Cerrando MSAD...")
                    self.stop_http_server()
                    break
                else:
                    print("Opción inválida. Intenta de nuevo.")
                    
        except KeyboardInterrupt:
            print("\nCerrando MSAD...")
            self.stop_http_server()
            sys.exit(0)
    
    def get_next_message(self, timeout=0.1):
        """Obtener el siguiente mensaje de la cola de notificaciones"""
        try:
            return self.message_queue.get(block=True, timeout=timeout)
        except:
            return None

# Función para iniciar el servidor directamente desde otro script
def start_msad(start_http=True):
    """Iniciar servidor MSAD desde otro script"""
    return MSADServer(start_http=start_http)

# Para ejecución directa del script
if __name__ == "__main__":
    print("Iniciando MSAD...")
    server = MSADServer()
    server.run_interactive() 