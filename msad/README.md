# MSAD - Microservicio de Almacenamiento Distribuido

## Descripción General

MSAD es un sistema ligero y autónomo para gestionar respaldos de la base de datos de RaspServer y compartirlos a través de un servidor HTTP integrado. Diseñado para funcionar tanto en Raspberry Pi como en Windows, este microservicio proporciona una solución simple pero efectiva para el almacenamiento y acceso a copias de seguridad.

## Estructura de Archivos

El módulo MSAD se compone de los siguientes archivos:

- `run_msad.py`: Aplicación principal que contiene toda la lógica para:
  - Crear respaldos de la base de datos
  - Iniciar y gestionar el servidor HTTP
  - Ofrecer una interfaz de menú interactiva
  
- `__init__.py`: Archivo que mantiene la carpeta como un módulo Python válido
  
- `index.html`: Página web que muestra el servidor HTTP, proporcionando una interfaz amigable para acceder a los respaldos

## Requisitos del Sistema

- **Python 3.6 o superior**: Necesario para ejecutar el script principal
- **SQLite3**: Utilizado para manejar los respaldos de la base de datos
- **Navegador web**: Para acceder a la interfaz HTTP desde otros dispositivos
- **Acceso a red local**: Para permitir que otros dispositivos accedan al servidor

## Instalación y Configuración

MSAD no requiere instalación especial. Simplemente asegúrese de:

1. Tener los archivos `run_msad.py`, `__init__.py` e `index.html` en la carpeta `msad` de su proyecto
2. Verificar que la base de datos de RaspServer existe y es accesible:
   - En Raspberry Pi: `/home/stevpi/Desktop/raspServer/sensor_data.db`
   - En Windows: `[ruta-del-proyecto]/sensor_data.db`

## Uso Detallado

### Iniciar MSAD

Para ejecutar el microservicio:

```bash
# En Windows (desde la carpeta principal del proyecto)
python msad/run_msad.py

# En Raspberry Pi
python3 msad/run_msad.py
```

### Menú Principal

Al iniciar, MSAD muestra un menú interactivo con las siguientes opciones:

1. **Crear respaldo manual**: 
   - Crea una copia de seguridad de la base de datos actual
   - El respaldo se almacena en la carpeta de respaldos diarios
   - Si se crea en domingo, también se guarda una copia en respaldos semanales
   - Si se crea el día 1 del mes, también se guarda una copia en respaldos mensuales

2. **Ver información del servidor**:
   - Muestra el estado actual del servidor HTTP (activo/inactivo)
   - Indica la URL completa para acceder al servidor
   - Presenta la ubicación de los directorios de almacenamiento
   - Muestra un recuento de los respaldos existentes (diarios, semanales, mensuales)

3. **Salir**:
   - Detiene el servidor HTTP
   - Cierra la aplicación

### Servidor HTTP Integrado

El servidor HTTP se inicia automáticamente al ejecutar MSAD y proporciona:

- Acceso a los respaldos desde cualquier dispositivo en la red local
- Una interfaz web amigable para navegar por los archivos
- URLs para descargar directamente los archivos de respaldo

Para acceder al servidor:
1. Abra un navegador en cualquier dispositivo conectado a la misma red
2. Ingrese la dirección: `http://IP-DEL-SERVIDOR:8080`
   - La IP se muestra al iniciar MSAD o en la opción "Ver información del servidor"
   - El puerto predeterminado es 8080

### Estructura de Respaldos

Los respaldos y datos se organizan de la siguiente manera:

**En Raspberry Pi**:
```
/mnt/storage/msad/
├── backups/
│   ├── daily/      # Respaldos diarios creados manualmente
│   ├── weekly/     # Respaldos semanales (domingos)
│   └── monthly/    # Respaldos mensuales (día 1)
└── index.html      # Página de inicio del servidor HTTP
```

**En Windows**:
```
[ruta-del-proyecto]/storage/msad/
├── backups/
│   ├── daily/      # Respaldos diarios creados manualmente
│   ├── weekly/     # Respaldos semanales (domingos)
│   └── monthly/    # Respaldos mensuales (día 1)
└── index.html      # Página de inicio del servidor HTTP
```

## Funcionamiento Técnico

### Detección Automática del Sistema

MSAD detecta automáticamente si se ejecuta en Windows o Raspberry Pi mediante:

```python
IS_WINDOWS = platform.system() == "Windows"
```

Esto permite configurar las rutas correctas para archivos y respaldos según el sistema operativo.

### Creación de Respaldos

El proceso de respaldo utiliza SQLite para crear una copia completa de la base de datos:

```python
conn = sqlite3.connect(DB_PATH)
with conn:
    conn.execute(f"VACUUM INTO '{backup_path}'")
conn.close()
```

Este método preserva la integridad de los datos al crear una copia exacta y optimizada de la base de datos.

### Servidor HTTP

El servidor utiliza el módulo `http.server` de Python para crear un servidor simple:

```python
handler = http.server.SimpleHTTPRequestHandler
self.httpd = socketserver.TCPServer(("", PORT), handler)
```

Esto proporciona un acceso básico a archivos con capacidades de navegación por directorios.

## Solución de Problemas

### Base de datos no encontrada

Si MSAD no encuentra la base de datos:
1. Verifique que la ruta a la base de datos sea correcta
2. Asegúrese de haber ejecutado primero la aplicación principal (app.py) para crear la base de datos
3. Compruebe los permisos de lectura/escritura en la ubicación de la base de datos

### No se puede acceder al servidor HTTP

Si no puede acceder al servidor desde otros dispositivos:
1. Verifique que ambos dispositivos estén en la misma red
2. Compruebe si hay algún firewall bloqueando el puerto 8080
3. Intente acceder usando la dirección IP local exacta mostrada en "Ver información del servidor"
4. Asegúrese de que MSAD sigue ejecutándose

### Problemas de permisos

En Raspberry Pi, si hay problemas para crear directorios o respaldos:
1. Verifique que el usuario tiene permisos de escritura en `/mnt/storage/`
2. Si el directorio no existe, puede necesitar crearlo manualmente con:
   ```bash
   sudo mkdir -p /mnt/storage/msad
   sudo chmod 755 /mnt/storage/msad
   sudo chown -R [su-usuario] /mnt/storage/msad
   ```

## Personalización Avanzada

Para personalizar MSAD, puede modificar directamente `run_msad.py` para:

- Cambiar el puerto del servidor HTTP (variable `PORT = 8080`)
- Modificar las rutas de almacenamiento (`STORAGE_DIR`)
- Añadir nuevas funcionalidades al menú principal
- Personalizar la frecuencia de los respaldos automáticos

## Limitaciones Actuales

- No implementa autenticación para el servidor HTTP
- No incluye compresión de respaldos
- No proporciona restauración automática desde respaldos
- No realiza respaldos programados (solo manuales) 