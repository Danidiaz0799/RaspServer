#!/usr/bin/env python3
"""
MSAD - Servidor de respaldos y acceso HTTP simple
Ejecuta este script cuando quieras activar MSAD
"""
import os
import sqlite3
import datetime
import http.server
import socketserver
import threading
import sys
import platform

# Detectar sistema operativo
IS_WINDOWS = platform.system() == "Windows"

# Configuración según el sistema operativo
if IS_WINDOWS:
    # Configuración para Windows
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
    DB_PATH = os.path.join(PROJECT_DIR, "sensor_data.db")
    STORAGE_DIR = os.path.join(PROJECT_DIR, "storage", "msad")
else:
    # Configuración para Raspberry Pi
    DB_PATH = "/home/stevpi/Desktop/raspServer/sensor_data.db"
    STORAGE_DIR = "/mnt/storage/msad"

PORT = 8080

class MSADServer:
    def __init__(self):
        # Crear directorios necesarios
        os.makedirs(os.path.join(STORAGE_DIR, "backups", "daily"), exist_ok=True)
        os.makedirs(os.path.join(STORAGE_DIR, "backups", "weekly"), exist_ok=True)
        os.makedirs(os.path.join(STORAGE_DIR, "backups", "monthly"), exist_ok=True)
        
        self.server_thread = None
        self.httpd = None
        self.running = False
    
    def start_http_server(self):
        """Iniciar el servidor HTTP"""
        def run():
            # Copiar el archivo index.html al directorio de almacenamiento
            index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
            if os.path.exists(index_path):
                import shutil
                shutil.copy2(index_path, os.path.join(STORAGE_DIR, "index.html"))
            
            os.chdir(STORAGE_DIR)
            handler = http.server.SimpleHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", PORT), handler)
            
            # Obtener la IP local para mostrarla
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            print(f"\nServidor HTTP iniciado en el puerto {PORT}")
            print(f"Accede desde: http://{ip}:{PORT}")
            print("CTRL+C para salir")
            
            self.running = True
            self.httpd.serve_forever()
            
        self.server_thread = threading.Thread(target=run)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop_http_server(self):
        """Detener el servidor HTTP"""
        if self.httpd and self.running:
            self.httpd.shutdown()
            self.running = False
            print("Servidor HTTP detenido")
    
    def create_backup(self):
        """Crear respaldo de la base de datos"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(STORAGE_DIR, "backups", "daily", f"sensor_data_{timestamp}.db")
            
            if os.path.exists(DB_PATH):
                # Crear respaldo con SQLite
                conn = sqlite3.connect(DB_PATH)
                with conn:
                    conn.execute(f"VACUUM INTO '{backup_path}'")
                conn.close()
                print(f"✓ Respaldo creado: {backup_path}")
                
                # Crear respaldos semanales y mensuales si es necesario
                now = datetime.datetime.now()
                
                # Verificar si es domingo (día 6)
                if now.weekday() == 6:
                    weekly_path = os.path.join(STORAGE_DIR, "backups", "weekly", f"sensor_data_{timestamp}.db")
                    import shutil
                    shutil.copy2(backup_path, weekly_path)
                    print(f"✓ Respaldo semanal creado: {weekly_path}")
                
                # Verificar si es día 1 del mes
                if now.day == 1:
                    monthly_path = os.path.join(STORAGE_DIR, "backups", "monthly", f"sensor_data_{timestamp}.db")
                    import shutil
                    shutil.copy2(backup_path, monthly_path)
                    print(f"✓ Respaldo mensual creado: {monthly_path}")
                
                return True
            else:
                print(f"✗ Error: Base de datos no encontrada: {DB_PATH}")
                print(f"  Si es la primera vez que ejecutas la aplicación, primero debes ejecutar app.py")
                print(f"  para crear la base de datos.")
                return False
        except Exception as e:
            print(f"✗ Error al crear respaldo: {str(e)}")
            return False

    def run(self):
        """Ejecutar MSAD con menú interactivo"""
        try:
            print("======================================")
            print("      MSAD - Sistema de Respaldos     ")
            print("======================================")
            print(f"Sistema: {platform.system()}")
            print(f"Base de datos: {DB_PATH}")
            print(f"Almacenamiento: {STORAGE_DIR}")
            
            # Verificar si existe la base de datos
            if not os.path.exists(DB_PATH):
                print("\n⚠️  ADVERTENCIA: Base de datos no encontrada.")
                print("   Primero debes ejecutar app.py para crear la base de datos.")
                print("   ¿Deseas continuar de todos modos? (s/n)")
                choice = input("   > ")
                if choice.lower() != 's':
                    print("Saliendo...")
                    return
            
            # Iniciar servidor HTTP
            self.start_http_server()
            
            # Menú principal
            while True:
                print("\n==== MSAD - Menú Principal ====")
                print("1. Crear respaldo manual")
                print("2. Ver información del servidor")
                print("3. Salir")
                
                choice = input("\nSelecciona una opción (1-3): ")
                
                if choice == "1":
                    self.create_backup()
                elif choice == "2":
                    print("\nInformación del servidor:")
                    print(f"- Estado: {'Activo' if self.running else 'Inactivo'}")
                    
                    # Obtener la IP local 
                    import socket
                    hostname = socket.gethostname()
                    ip = socket.gethostbyname(hostname)
                    print(f"- URL de acceso: http://{ip}:{PORT}")
                    
                    print(f"- Directorio de datos: {STORAGE_DIR}")
                    print(f"- Base de datos: {DB_PATH}")
                    
                    # Contar respaldos existentes
                    try:
                        daily_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "daily")) if f.endswith(".db")])
                        weekly_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "weekly")) if f.endswith(".db")])
                        monthly_count = len([f for f in os.listdir(os.path.join(STORAGE_DIR, "backups", "monthly")) if f.endswith(".db")])
                        print(f"- Respaldos: {daily_count} diarios, {weekly_count} semanales, {monthly_count} mensuales")
                    except:
                        print("- No se pudieron contar los respaldos")
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

if __name__ == "__main__":
    print("Iniciando MSAD...")
    # Crear los directorios necesarios
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server = MSADServer()
    server.run() 