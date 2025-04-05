# MSAD - Microservicio de Almacenamiento Distribuido

## Descripción

MSAD es un microservicio que gestiona respaldos automáticos de la base de datos, exportaciones y almacenamiento distribuido para el proyecto RaspServer. Proporciona una interfaz HTTP para acceder a los respaldos y datos almacenados.

## Estructura del Módulo

El módulo MSAD ha sido organizado de forma modular y con nombres descriptivos para maximizar la escalabilidad, mantenibilidad y claridad visual:

```
msad/
├── __init__.py                # Importación minimalista
├── msad_main.py               # Punto de entrada principal
├── run_msad.py                # Script ejecutable
├── config/
│   ├── __init__.py            # Inicialización mínima
│   ├── app_settings.py        # Variables y parámetros de configuración
│   └── config_exports.py      # Exportaciones centralizadas de configuración
├── core/
│   ├── __init__.py            # Inicialización mínima
│   ├── backup_manager.py      # Operaciones de respaldo
│   ├── system_utils.py        # Sistema y funciones auxiliares
│   └── core_exports.py        # Exportaciones centralizadas del core
├── api/
│   ├── __init__.py            # Inicialización mínima
│   ├── flask_routes.py        # Definición de endpoints Flask
│   └── api_exports.py         # Exportaciones centralizadas de la API
├── server/
│   ├── __init__.py            # Inicialización mínima
│   ├── web_server.py          # Implementación del servidor HTTP
│   └── server_exports.py      # Exportaciones centralizadas del servidor
└── index.html                 # Página web para el servidor HTTP
```

## Uso

### Uso dentro de RaspServer

```python
from msad import init_msad, shutdown_msad, create_backup, get_msad_status

# Inicializar MSAD
status = init_msad(auto_backup=True, backup_interval_hours=24)
print(f"Estado MSAD: {status}")

# Crear un respaldo manual
backup_result = create_backup()

# Obtener estado actual
status = get_msad_status()

# Al cerrar la aplicación
shutdown_msad()
```

### Uso como servicio independiente

```bash
python -m msad.run_msad
```

### Integración con Flask

```python
from msad import create_msad_blueprint

# Crear y registrar el blueprint
msad_bp = create_msad_blueprint()
app.register_blueprint(msad_bp, url_prefix='/api')
```

## Rutas API

- `GET /api/msad/status`: Obtener estado del servicio
- `POST /api/msad/backup`: Crear respaldo manual
- `POST /api/msad/restart`: Reiniciar el servicio
- `GET /api/clients/<client_id>/msad/stats`: Estadísticas para cliente específico

## Configuración

Las rutas y comportamiento de MSAD se pueden configurar en el archivo `config/app_settings.py`.

## Desarrollo

Para extender la funcionalidad de MSAD, se recomienda seguir la estructura modular existente:

1. Añadir funcionalidad en los archivos principales:
   - Nuevas configuraciones en `config/app_settings.py`
   - Funcionalidad de respaldo en `core/backup_manager.py`
   - Utilidades del sistema en `core/system_utils.py`
   - Endpoints API en `api/flask_routes.py`
   - Funcionalidad del servidor en `server/web_server.py`

2. Exportar las nuevas funciones:
   - Añadir exportaciones en el archivo `*_exports.py` correspondiente
   - Los archivos `__init__.py` no necesitan modificación 