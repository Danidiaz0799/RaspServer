# 📊 MSAD - Microservicio de Almacenamiento y Datos

<div align="center">

![Versión](https://img.shields.io/badge/Versión-1.0.0--minimal-blue)
![Integración](https://img.shields.io/badge/Integración-RaspServer-green)
![Estado](https://img.shields.io/badge/Estado-Activo-brightgreen)

</div>

## 📋 Índice

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Funcionalidades](#-funcionalidades)
- [Integración con RaspServer](#-integración-con-raspserver)
- [API Reference](#-api-reference)
- [Ejemplos Prácticos](#-ejemplos-prácticos)
- [Esquema de Almacenamiento](#-esquema-de-almacenamiento)
- [Flujo de Trabajo](#-flujo-de-trabajo)
- [Solución de Problemas](#-solución-de-problemas)
- [Desarrollo Futuro](#-desarrollo-futuro)

## 📝 Descripción

MSAD es un **microservicio optimizado** para generación y gestión de reportes que se integra perfectamente con RaspServer. Permite extraer, filtrar y exportar datos críticos del cultivo de hongos para facilitar análisis detallados y toma de decisiones.

### ✨ Características Clave

| Característica | Descripción |
|----------------|-------------|
| 🚀 **Alta Performance** | Consultas optimizadas y bajo impacto en recursos |
| 🔄 **Formatos Múltiples** | Exportación en JSON y CSV para máxima compatibilidad |
| 🔍 **Filtrado Avanzado** | Selección por cliente, fechas, tipo de datos |
| 📊 **Análisis de Datos** | Facilita la comprensión de tendencias y patrones |
| 🔗 **Integración Simple** | API RESTful con endpoints intuitivos |

## 🏗 Arquitectura

MSAD implementa una arquitectura minimalista y eficiente:

```
                    ┌───────────────────┐
                    │                   │
                    │   Flask Server    │
                    │   (app.py)        │
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────┐
│                      MSAD                           │
│                                                     │
│  ┌───────────────┐         ┌────────────────────┐  │
│  │               │         │                    │  │
│  │  API Layer    │ ◄────► │     Core Layer     │  │
│  │ simple_routes │         │ system + reports   │  │
│  │               │         │                    │  │
│  └───────────────┘         └────────────────────┘  │
│          ▲                          │              │
└──────────┼──────────────────────────┼──────────────┘
           │                          ▼
┌──────────┴──────────┐    ┌──────────────────────┐
│                     │    │                      │
│  Cliente/Frontend   │    │    Base de Datos     │
│                     │    │    (SQLite)          │
└─────────────────────┘    └──────────────────────┘
```

### 📁 Estructura de Código Simplificada

```
msad/
├── __init__.py           # Importación principal
├── api/
│   ├── __init__.py       # Configuración API
│   └── simple_routes.py  # Endpoints RESTful
└── core/
    ├── __init__.py       # Configuración core
    ├── reports.py        # Generación de reportes
    └── system.py         # Funciones del sistema
```

## 🎯 Funcionalidades

MSAD ofrece las siguientes funcionalidades clave para el monitoreo y análisis de cultivos:

### 📊 Generación de Reportes

Extrae datos de la base de datos y genera reportes en formato JSON o CSV con información detallada sobre:

- **Datos de Sensores**: Temperatura y humedad del ambiente de cultivo
- **Acciones de Actuadores**: Registro de activaciones de ventiladores, humidificadores, etc.
- **Eventos del Sistema**: Alertas, notificaciones y cambios de estado

### 🔎 Consulta y Filtrado

Permite búsqueda avanzada por:
- **Cliente/Cultivo**: Filtra información por ubicación o proyecto específico
- **Rango de Fechas**: Análisis de períodos concretos
- **Tipo de Datos**: Enfoque en sensores, actuadores o eventos
- **Formato**: Elección entre JSON para aplicaciones o CSV para análisis en hojas de cálculo

### 💾 Gestión de Archivos

- **Almacenamiento Optimizado**: Organiza reportes por cliente y tipo
- **Descarga Directa**: Acceso simple a los archivos generados
- **Listado de Reportes**: Visualización del historial de informes

### 🔄 Backups Automáticos

Protección integral de datos mediante:
- **Backups Programados**: Copias de seguridad automáticas en intervalos configurables
- **Backups Manuales**: Posibilidad de crear copias de seguridad bajo demanda
- **Rotación Inteligente**: Mantiene un número limitado de backups para optimizar espacio
- **Verificación de Integridad**: Comprueba la integridad de la base de datos antes de crear copias
- **Restauración Segura**: Sistema de restauración con copia de seguridad previa
- **Gestión Completa**: Interfaz API para listar, descargar y eliminar backups

## 🔌 Integración con RaspServer

MSAD se integra con RaspServer a través de los siguientes puntos:

### 1️⃣ Registro de Blueprint

En `app.py` se registra el blueprint de MSAD para habilitar los endpoints:

```python
from msad.api.simple_routes import create_msad_blueprint, create_export_blueprint

# Crear y registrar los blueprints
msad_bp = create_msad_blueprint()
reports_bp = create_export_blueprint()

app.register_blueprint(msad_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
```

### 2️⃣ Acceso a Datos

MSAD accede a la misma base de datos que utiliza RaspServer para los sensores:

```python
# En msad/core/system.py
def get_database_path():
    if os.name == 'nt':  # Windows
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "sensor_data.db")
    else:  # Linux
        return "/home/stevpi/Desktop/raspServer/sensor_data.db"
```

### 3️⃣ Flujo de Datos en RaspServer

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Sensores SHT3x │ ───► │  Base de Datos  │ ◄───  │  MSAD Reports   │
│  (MQTT Client)  │       │   (SQLite)      │       │  (Exportación)  │
│                 │       │                 │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   ▲
                                   │
                          ┌────────┴────────┐
                          │                 │
                          │  API Endpoints  │
                          │  (Flask)        │
                          │                 │
                          └─────────────────┘
                                   ▲
                                   │
                          ┌────────┴────────┐
                          │                 │
                          │  Cliente Web    │
                          │  (Frontend)     │
                          │                 │
                          └─────────────────┘
```

## 📘 API Reference

### 🟢 Estado del Servicio

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/msad/status</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Obtiene el estado actual del servicio MSAD</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>Ninguno</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "service": "msad",
  "version": "1.0.0-minimal",
  "status": "running"
}
```

</td>
</tr>
</table>

### 🔷 Sistema de Backups

#### 🔹 Listar Backups

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/msad/backups</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Lista todos los backups disponibles de la base de datos</td>
</tr>
<tr>
<td><strong>Parámetros Query</strong></td>
<td>
• <code>type</code> (opcional): Filtrar por tipo de backup ("manual" o "auto")
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "backups": [
    {
      "backup_id": "backup_20230405_143020",
      "filename": "sensor_data_manual_20230405_143020.db",
      "type": "manual",
      "size": 512000,
      "created_at": "2023-04-05T14:30:20.123456",
      "download_url": "/api/msad/backups/download/sensor_data_manual_20230405_143020.db"
    }
  ],
  "total": 1
}
```

</td>
</tr>
</table>

#### 🔹 Crear Backup Manual

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>POST /api/msad/backups/create</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Crea un backup manual de la base de datos</td>
</tr>
<tr>
<td><strong>Cuerpo</strong></td>
<td>Ninguno</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "backup_id": "backup_20230405_143020",
  "filename": "sensor_data_manual_20230405_143020.db",
  "path": "/mnt/storage/msad/backups/sensor_data_manual_20230405_143020.db",
  "size": 512000,
  "type": "manual",
  "created_at": "2023-04-05T14:30:20.123456",
  "download_url": "/api/msad/backups/download/sensor_data_manual_20230405_143020.db"
}
```

</td>
</tr>
</table>

#### 🔹 Descargar Backup

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/msad/backups/download/{filename}</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Descarga un archivo de backup específico</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>filename</code>: Nombre del archivo de backup
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>
• <strong>Éxito</strong>: Archivo binario de la base de datos de backup<br>
• <strong>Content-Type</strong>: "application/octet-stream"<br>
• <strong>Content-Disposition</strong>: attachment; filename="nombre_archivo"<br><br>
En caso de error:
```json
{
  "success": false,
  "error": "Archivo de backup no encontrado"
}
```
</td>
</tr>
</table>

#### 🔹 Eliminar Backup

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>DELETE /api/msad/backups/{filename}</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Elimina un backup específico</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>filename</code>: Nombre del archivo de backup
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "message": "Backup sensor_data_manual_20230405_143020.db eliminado correctamente"
}
```

</td>
</tr>
</table>

#### 🔹 Restaurar Backup

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>POST /api/msad/backups/restore/{filename}</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Restaura un backup a la base de datos actual</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>filename</code>: Nombre del archivo de backup
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "message": "Backup sensor_data_manual_20230405_143020.db restaurado correctamente",
  "safety_backup": "sensor_data_manual_20230406_103045.db"
}
```

</td>
</tr>
</table>

#### 🔹 Estado del Programador de Backups

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/msad/backups/scheduler</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Obtiene el estado actual del programador de backups automáticos</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>Ninguno</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "is_running": true,
  "backup_count": 5,
  "total_size": 2560000,
  "formatted_size": "2.44 MB",
  "last_backup": "2023-04-05T14:30:20.123456",
  "next_backup": "2023-04-06T14:30:20.123456",
  "backup_dir": "/mnt/storage/msad/backups"
}
```

</td>
</tr>
</table>

#### 🔹 Configurar Programador de Backups

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>POST /api/msad/backups/scheduler</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Configura el programador de backups automáticos</td>
</tr>
<tr>
<td><strong>Cuerpo</strong></td>
<td>

```json
{
  "enabled": true,
  "interval_hours": 24
}
```

</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>enabled</code> (opcional): Activar/desactivar backups automáticos (default: true)<br>
• <code>interval_hours</code> (opcional): Intervalo en horas entre backups (default: 24)
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "message": "Programador de backups iniciado con intervalo de 24 horas",
  "status": {
    "is_running": true,
    "backup_count": 5,
    "total_size": 2560000,
    "formatted_size": "2.44 MB",
    "last_backup": "2023-04-05T14:30:20.123456",
    "next_backup": "2023-04-06T14:30:20.123456",
    "backup_dir": "/mnt/storage/msad/backups"
  }
}
```

</td>
</tr>
</table>

### 🔵 Crear Datos de Prueba

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>POST /api/msad/test-data</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Inserta datos aleatorios para pruebas</td>
</tr>
<tr>
<td><strong>Cuerpo</strong></td>
<td>

```json
{
  "client_id": "mushroom1",
  "count": 20
}
```

</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>client_id</code> (opcional): ID del cliente (default: "mushroom1")<br>
• <code>count</code> (opcional): Número de registros (default: 10)
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "message": "Se insertaron 20 registros de prueba para el cliente mushroom1",
  "count": 20
}
```

</td>
</tr>
</table>

### 🟠 Generar Reporte

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>POST /api/clients/{client_id}/msad/reports</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Genera un reporte con los datos especificados</td>
</tr>
<tr>
<td><strong>Cuerpo</strong></td>
<td>

```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-05-01",
  "data_type": "sensors",
  "format": "json"
}
```

</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>start_date</code> (obligatorio): Fecha inicial (YYYY-MM-DD)<br>
• <code>end_date</code> (obligatorio): Fecha final (YYYY-MM-DD)<br>
• <code>data_type</code> (opcional): Tipo de datos ("sensors", "events", "actuators")<br>
• <code>format</code> (opcional): Formato del archivo ("json", "csv")
</td>
</tr>
<tr>
<td><strong>Respuesta Exitosa</strong></td>
<td>

```json
{
  "success": true,
  "client_id": "mushroom1",
  "created_at": "2025-04-05T02:20:20.775557",
  "data_type": "sensors",
  "download_url": "/api/clients/mushroom1/msad/reports/download/mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json",
  "filename": "mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json",
  "format": "json",
  "period": {
    "end": "2025-05-01",
    "start": "2025-01-01"
  },
  "records": 3888,
  "report_id": "report_20250405_022020",
  "size": 596838
}
```

</td>
</tr>
<tr>
<td><strong>Respuesta Error</strong></td>
<td>

```json
{
  "success": false,
  "error": "No se encontraron datos para el rango especificado"
}
```

</td>
</tr>
</table>

### 🟣 Listar Reportes de un Cliente

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/clients/{client_id}/msad/reports</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Lista todos los reportes disponibles para un cliente específico</td>
</tr>
<tr>
<td><strong>Parámetros Query</strong></td>
<td>
• <code>format</code> (opcional): Filtrar por formato ("json", "csv")<br>
• <code>data_type</code> (opcional): Filtrar por tipo de datos ("sensors", "events", "actuators")
</td>
</tr>
<tr>
<td><strong>Ejemplo</strong></td>
<td><code>GET /api/clients/mushroom1/msad/reports?format=json&data_type=sensors</code></td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>

```json
{
  "success": true,
  "reports": [
    {
      "report_id": "report_20250405_022020",
      "client_id": "mushroom1",
      "data_type": "sensors",
      "filename": "mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json",
      "format": "json",
      "size": 596838,
      "created_at": "2025-04-05T02:20:20.775557",
      "download_url": "/api/clients/mushroom1/msad/reports/download/mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json"
    }
  ],
  "total": 1
}
```

</td>
</tr>
</table>

### 🔴 Listar Todos los Reportes

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/msad/reports</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Lista todos los reportes disponibles para todos los clientes</td>
</tr>
<tr>
<td><strong>Parámetros Query</strong></td>
<td>
• <code>format</code> (opcional): Filtrar por formato ("json", "csv")<br>
• <code>data_type</code> (opcional): Filtrar por tipo de datos ("sensors", "events", "actuators")
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>Similar a la del endpoint anterior, pero incluye reportes de todos los clientes</td>
</tr>
</table>

### ⚪ Descargar Reporte

<table>
<tr>
<td><strong>Endpoint</strong></td>
<td><code>GET /api/clients/{client_id}/msad/reports/download/{filename}</code></td>
</tr>
<tr>
<td><strong>Descripción</strong></td>
<td>Descarga un archivo de reporte específico</td>
</tr>
<tr>
<td><strong>Parámetros</strong></td>
<td>
• <code>client_id</code>: ID del cliente<br>
• <code>filename</code>: Nombre del archivo a descargar
</td>
</tr>
<tr>
<td><strong>Respuesta</strong></td>
<td>
• <strong>Éxito</strong>: Archivo binario con el contenido del reporte<br>
• <strong>Content-Type</strong>: "application/json" o "text/csv" según el formato<br>
• <strong>Content-Disposition</strong>: attachment; filename="nombre_archivo"<br><br>
En caso de error:
```json
{
  "success": false,
  "error": "Archivo no encontrado"
}
```
</td>
</tr>
</table>

## 📋 Tabla de Tipos de Datos y Formatos

<table>
<tr>
<th colspan="2">Tipos de Datos Disponibles</th>
</tr>
<tr>
<td><strong>Valor</strong></td>
<td><strong>Descripción</strong></td>
</tr>
<tr>
<td><code>sensors</code></td>
<td>Datos de sensores SHT3x (temperatura y humedad)</td>
</tr>
<tr>
<td><code>events</code></td>
<td>Eventos del sistema y alertas</td>
</tr>
<tr>
<td><code>actuators</code></td>
<td>Acciones de actuadores (ventiladores, iluminación, etc.)</td>
</tr>

<tr>
<th colspan="2">Formatos de Reporte</th>
</tr>
<tr>
<td><strong>Valor</strong></td>
<td><strong>Descripción</strong></td>
</tr>
<tr>
<td><code>json</code></td>
<td>Formato JSON estructurado (ideal para aplicaciones)</td>
</tr>
<tr>
<td><code>csv</code></td>
<td>Formato CSV para importación en hojas de cálculo</td>
</tr>
</table>

## 🚀 Ejemplos Prácticos

### 📡 Consulta de Estado

```bash
# Verificar que el servicio esté activo
curl -X GET http://192.168.137.214:5000/api/msad/status

# Respuesta esperada:
# {
#   "success": true,
#   "service": "msad",
#   "version": "1.0.0-minimal",
#   "status": "running"
# }
```

### 🧪 Creación de Datos de Prueba

```bash
# Generar 30 registros para el cliente "mushroom1"
curl -X POST http://192.168.137.214:5000/api/msad/test-data \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "mushroom1",
    "count": 30
  }'

# Respuesta esperada:
# {
#   "success": true,
#   "message": "Se insertaron 30 registros de prueba para el cliente mushroom1",
#   "count": 30
# }
```

### 📊 Generación de Reportes

```bash
# Crear un reporte JSON para un período específico
curl -X POST http://192.168.137.214:5000/api/clients/mushroom1/msad/reports \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01",
    "end_date": "2025-05-01",
    "data_type": "sensors",
    "format": "json"
  }'

# Crear un reporte CSV para análisis en Excel
curl -X POST http://192.168.137.214:5000/api/clients/mushroom1/msad/reports \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01",
    "end_date": "2025-05-01",
    "data_type": "sensors",
    "format": "csv"
  }'
```

### 🔎 Filtrado de Reportes

```bash
# Listar solo reportes JSON
curl -X GET "http://192.168.137.214:5000/api/clients/mushroom1/msad/reports?format=json"

# Listar solo reportes de eventos
curl -X GET "http://192.168.137.214:5000/api/clients/mushroom1/msad/reports?data_type=events"

# Combinando múltiples filtros
curl -X GET "http://192.168.137.214:5000/api/clients/mushroom1/msad/reports?format=json&data_type=sensors"
```

### 💾 Descarga de Reportes

```bash
# Descargar un reporte específico
curl -X GET -O "http://192.168.137.214:5000/api/clients/mushroom1/msad/reports/download/mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json"
```

### 💾 Gestión de Backups

```bash
# Listar todos los backups disponibles
curl -X GET "http://192.168.137.214:5000/api/msad/backups"

# Filtrar solo backups manuales
curl -X GET "http://192.168.137.214:5000/api/msad/backups?type=manual"

# Crear un backup manual
curl -X POST "http://192.168.137.214:5000/api/msad/backups/create"

# Descargar un backup específico
curl -X GET -O "http://192.168.137.214:5000/api/msad/backups/download/sensor_data_manual_20230405_143020.db"

# Eliminar un backup
curl -X DELETE "http://192.168.137.214:5000/api/msad/backups/sensor_data_manual_20230405_143020.db"

# Restaurar un backup
curl -X POST "http://192.168.137.214:5000/api/msad/backups/restore/sensor_data_manual_20230405_143020.db"
```

### ⏱️ Configuración de Backups Automáticos

```bash
# Obtener estado actual del programador de backups
curl -X GET "http://192.168.137.214:5000/api/msad/backups/scheduler"

# Configurar backups automáticos cada 12 horas
curl -X POST "http://192.168.137.214:5000/api/msad/backups/scheduler" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "interval_hours": 12
  }'

# Desactivar backups automáticos
curl -X POST "http://192.168.137.214:5000/api/msad/backups/scheduler" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

## 📂 Esquema de Almacenamiento

Los reportes y backups se organizan en una estructura jerárquica para facilitar su acceso y gestión:

```
┌─ /mnt/storage/msad/
│  │
│  ├─ reports/
│  │  │
│  │  ├─ mushroom1/
│  │  │  ├─ mushroom1_sensors_2025-01-01_to_2025-05-01_20250405_022020.json
│  │  │  ├─ mushroom1_events_2025-02-01_to_2025-03-01_20250406_103045.csv
│  │  │  └─ ...
│  │  │
│  │  ├─ mushroom2/
│  │  │  ├─ mushroom2_sensors_2025-01-15_to_2025-02-15_20250410_143020.json
│  │  │  └─ ...
│  │  │
│  │  └─ ...
│  │
│  ├─ backups/
│  │  ├─ sensor_data_auto_20230401_000000.db
│  │  ├─ sensor_data_manual_20230405_143020.db
│  │  └─ ...
│  │
│  └─ logs/
│     └─ msad.log
```

**En desarrollo (Windows):**
```
RaspServer/storage/msad/reports/{client_id}/{filename}
RaspServer/storage/msad/backups/{filename}
```

**En producción (Linux):**
```
/mnt/storage/msad/reports/{client_id}/{filename}
/mnt/storage/msad/backups/{filename}
```

## 🔄 Flujo de Trabajo

El siguiente diagrama muestra los flujos de trabajo principales en MSAD:

### 📊 Generación y Consulta de Reportes

```
┌──────────────┐      ┌──────────────────┐      ┌───────────────────┐
│              │      │                  │      │                   │
│ 1. Verificar │      │ 2. Generar datos │      │ 3. Crear reporte  │
│    estado    │ ───► │    de prueba     │ ───► │    con filtros    │
│              │      │    (opcional)    │      │                   │
└──────────────┘      └──────────────────┘      └─────────┬─────────┘
                                                          │
                                                          ▼
┌──────────────┐      ┌──────────────────┐      ┌───────────────────┐
│              │      │                  │      │                   │
│ 6. Analizar  │      │ 5. Descargar     │      │ 4. Listar         │
│    datos     │ ◄─── │    reporte       │ ◄─── │    reportes       │
│              │      │                  │      │                   │
└──────────────┘      └──────────────────┘      └───────────────────┘
```

### 💾 Proceso de Backup y Restauración

```
┌──────────────┐      ┌──────────────────┐      ┌───────────────────┐
│              │      │                  │      │                   │
│ 1. Configurar│      │ 2. Crear backup  │      │ 3. Listar         │
│   scheduler  │ ───► │    manual/auto   │ ───► │    backups        │
│              │      │                  │      │                   │
└──────────────┘      └──────────────────┘      └─────────┬─────────┘
                                                          │
                                                          ▼
                      ┌──────────────────┐      ┌───────────────────┐
                      │                  │      │                   │
                      │ 5. Restaurar     │ ◄─── │ 4. Descargar      │
                      │    backup        │      │    backup         │
                      │    (si necesario)│      │    (si necesario) │
                      └──────────────────┘      └───────────────────┘
```

## ❓ Solución de Problemas

<table>
<tr>
<th>Problema</th>
<th>Causa Probable</th>
<th>Solución</th>
</tr>
<tr>
<td>"No se encontraron datos para el rango especificado"</td>
<td>No hay datos en el rango de fechas seleccionado</td>
<td>
• Verifica que el rango de fechas sea correcto<br>
• Crea datos de prueba con el endpoint <code>/api/msad/test-data</code><br>
• Asegúrate de que el cliente existe en la base de datos
</td>
</tr>
<tr>
<td>"Error al consultar la base de datos"</td>
<td>Problema al acceder a la base de datos</td>
<td>
• Verifica que la base de datos existe en la ruta correcta<br>
• Asegúrate de que no haya bloqueos en la BD<br>
• Revisa los logs en <code>/mnt/storage/msad/logs/msad.log</code>
</td>
</tr>
<tr>
<td>"Archivo no encontrado" al descargar</td>
<td>El archivo solicitado no existe o fue eliminado</td>
<td>
• Verifica que el nombre de archivo sea correcto<br>
• Comprueba que el directorio de almacenamiento existe<br>
• Regenera el reporte si es necesario
</td>
</tr>
<tr>
<td>Error en el formato de fecha</td>
<td>Formato de fecha incorrecto</td>
<td>
• Usa el formato YYYY-MM-DD (ejemplo: 2025-05-01)<br>
• Asegúrate de que la fecha final sea posterior a la inicial
</td>
</tr>
<tr>
<td>"La base de datos está corrupta y no se puede realizar el backup"</td>
<td>Problemas de integridad en la base de datos</td>
<td>
• Restaura un backup previo si está disponible<br>
• Verifica los permisos de la base de datos<br>
• Ejecuta <code>PRAGMA integrity_check</code> directamente en la BD
</td>
</tr>
<tr>
<td>El programador de backups no inicia</td>
<td>Problemas con la biblioteca schedule o permisos</td>
<td>
• Verifica que schedule está instalado (<code>pip install schedule</code>)<br>
• Revisa los logs en busca de errores detallados<br>
• Verifica que el directorio de backups tiene permisos de escritura
</td>
</tr>
<tr>
<td>No se pueden restaurar backups</td>
<td>Problemas de permisos o base de datos en uso</td>
<td>
• Asegúrate de que la base de datos no está siendo usada por otro proceso<br>
• Verifica que el usuario tiene permisos de escritura<br>
• Intenta detener y reiniciar el servidor antes de restaurar
</td>
</tr>
</table>

## 🔮 Desarrollo Futuro

### Posibles Mejoras Futuras

- **Exportación a más formatos**: PDF, XLSX para reportes más formales
- **Análisis estadístico incorporado**: Agregar estadísticas básicas a los reportes
- **Reportes programados**: Generación automática periódica
- **Notificaciones**: Avisos por email al completarse reportes extensos
- **Compresión**: Compresión automática de reportes grandes
- **Visualizaciones**: Generar gráficos básicos junto con los datos

### Extensión de Código

Para añadir nuevas funcionalidades:

```python
# En msad/core/reports.py - Añadir nuevo tipo de reporte:
def generate_statistics_report(client_id, start_date, end_date, format="json"):
    """
    Generar reporte de estadísticas para un cliente en un rango de fechas
    """
    # Implementación
    pass

# En msad/api/simple_routes.py - Añadir nuevo endpoint:
@reports_bp.route('/clients/<client_id>/msad/statistics', methods=['POST'])
def create_statistics_report(client_id):
    """Endpoint para crear estadísticas"""
    # Implementación
    pass
```

## 💻 Instalación y Requisitos

Para instalar y utilizar el sistema de backups automáticos, asegúrate de cumplir con los siguientes requisitos:

### Dependencias

```bash
# Instalar dependencias
pip install flask aiosqlite paho-mqtt schedule
```

El archivo `requirements.txt` incluye todas las dependencias necesarias:

```
flask>=2.0.0
aiosqlite>=0.17.0
paho-mqtt>=1.5.0
schedule>=1.1.0  # Para backups automáticos programados
```

### Activar Backups Automáticos

Para habilitar los backups automáticos al iniciar la aplicación, modifica la línea en `app.py` donde se inicializa MSAD:

```python
# Inicializar MSAD con backups automáticos cada 24 horas
status = init_msad(auto_backup=True, backup_interval_hours=24)
```

### Permisos de Directorios

Asegúrate de que la aplicación tenga permisos de escritura en los directorios de almacenamiento:

```bash
# En sistemas Linux/Raspberry Pi
sudo mkdir -p /mnt/storage/msad/backups
sudo chown -R [usuario]:users /mnt/storage/msad
```

---

<div align="center">
   
   **MSAD** - Documentación v1.0.0 - Desarrollado para RaspServer

</div> 