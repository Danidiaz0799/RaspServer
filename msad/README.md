# MSAD - Microservicio de Almacenamiento Distribuido

## Descripción General

MSAD es un sistema ligero y autónomo para gestionar respaldos de la base de datos de RaspServer y compartirlos a través de un servidor HTTP integrado. Diseñado para funcionar tanto en Raspberry Pi como en Windows, este microservicio proporciona una solución simple pero efectiva para el almacenamiento y acceso a copias de seguridad.

## Estructura de Archivos

El módulo MSAD se compone de los siguientes archivos:

- `config.py`: Configuración centralizada utilizada por todos los componentes
- `server.py`: Implementación del servidor y funcionalidades de respaldo
- `integration.py`: Facilita la integración con RaspServer
- `run_msad.py`: Script para ejecutar MSAD de forma independiente
- `__init__.py`: Archivo que mantiene la carpeta como un módulo Python válido
- `index.html`: Página web para el servidor HTTP

## Requisitos del Sistema

- **Python 3.6 o superior**: Necesario para ejecutar el script principal
- **SQLite3**: Utilizado para manejar los respaldos de la base de datos
- **Navegador web**: Para acceder a la interfaz HTTP desde otros dispositivos
- **Acceso a red local**: Para permitir que otros dispositivos accedan al servidor

## Uso Detallado

### Modo Independiente

Para ejecutar MSAD como aplicación independiente:

```bash
# En Windows (desde la carpeta principal del proyecto)
python msad/run_msad.py

# En Raspberry Pi
python3 msad/run_msad.py
```

### Integración con RaspServer

MSAD puede integrarse directamente con RaspServer. Simplemente añade estas líneas a tu archivo `app.py`:

```python
# Al inicio del archivo, añadir:
from msad.integration import init_msad, shutdown_msad, create_backup, get_msad_status

# Después de inicializar la app Flask:
msad_status = init_msad(auto_backup=True, backup_interval_hours=24)
print(f"Estado de MSAD: {msad_status['message']}")

# Registrar función de limpieza al salir (opcional, ya lo hace init_msad):
# atexit.register(shutdown_msad)
```

Esto iniciará automáticamente MSAD cuando arranque RaspServer.

### API para RaspServer

La integración proporciona estas funciones:

- `init_msad()`: Inicializa el servidor MSAD
- `shutdown_msad()`: Detiene el servidor y libera recursos
- `create_backup()`: Crea un respaldo manual
- `get_msad_status()`: Obtiene información del estado actual

### Menú Principal (en modo independiente)

Al iniciar MSAD, muestra un menú interactivo con las siguientes opciones:

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

## Configuración

Todos los ajustes están centralizados en `config.py`:

```python
# Ejemplo de configuración
DATABASE_PATH = "/home/stevpi/Desktop/raspServer/sensor_data.db"
STORAGE_DIR = "/mnt/storage/msad"
HTTP_PORT = 8080
BACKUP_RETENTION = {
    "daily": 7,    # Número de respaldos diarios a mantener
    "weekly": 4,   # Número de respaldos semanales a mantener
    "monthly": 6   # Número de respaldos mensuales a mantener
}
```

### Limpieza Automática

MSAD incluye limpieza automática de respaldos antiguos según la política definida en `config.py`.

## Estructura de Respaldos

Los respaldos y datos se organizan de la siguiente manera:

```
/mnt/storage/msad/ (o C:\ruta\proyecto\storage\msad en Windows)
├── backups/
│   ├── daily/      # Respaldos diarios 
│   ├── weekly/     # Respaldos semanales (domingos)
│   └── monthly/    # Respaldos mensuales (día 1)
└── index.html      # Página de inicio del servidor HTTP
```

## Comunicación entre RaspServer y MSAD

MSAD utiliza un sistema de colas (`Queue`) para la comunicación entre componentes:

- Al crear un respaldo, MSAD envía un mensaje a la cola
- Al iniciar/detener el servidor, se envían mensajes de estado
- El sistema de integración captura estos mensajes y actúa en consecuencia

## Solución de Problemas

### Base de datos no encontrada

Si MSAD no encuentra la base de datos:
1. Verifique la ruta en `config.py`
2. Asegúrese de haber ejecutado primero la aplicación principal
3. Compruebe los permisos de lectura/escritura

### No se puede acceder al servidor HTTP

Si no puede acceder al servidor desde otros dispositivos:
1. Verifique que ambos dispositivos estén en la misma red
2. Compruebe si hay algún firewall bloqueando el puerto 8080
3. Intente acceder usando la dirección IP local exacta mostrada en el panel
4. Asegúrese de que MSAD sigue ejecutándose

### Problemas de permisos

En Raspberry Pi, si hay problemas para crear directorios o respaldos:
1. Verifique que el usuario tiene permisos de escritura
2. Si el directorio no existe, puede necesitar crearlo manualmente

## Personalización Avanzada

Para personalizar MSAD, modifique el archivo `config.py` para:

- Cambiar el puerto del servidor HTTP
- Modificar las rutas de almacenamiento
- Ajustar la política de retención de respaldos
- Cambiar el intervalo de respaldos automáticos 