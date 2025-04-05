# MSAD - Microservicio de Almacenamiento y Datos

## Descripción

MSAD es un microservicio simplificado y optimizado que proporciona generación y gestión de reportes para el proyecto RaspServer. Este sistema permite extraer, filtrar y exportar datos de sensores, eventos y actuadores para facilitar el análisis y monitoreo de cultivos de hongos.

## Ventajas

- **Interfaz Simple**: API RESTful intuitiva y fácil de usar
- **Mínima Sobrecarga**: Arquitectura simplificada para máximo rendimiento
- **Formatos Flexibles**: Soporte para exportación en JSON y CSV
- **Filtrado por Cliente**: Reportes específicos por cada cultivo/cliente
- **Consultas Optimizadas**: Bajo impacto en la base de datos principal
- **Mantenimiento Reducido**: Menos dependencias, menos puntos de fallo

## ¿Por qué MSAD en RaspServer?

RaspServer necesitaba una forma eficiente de:
1. **Extraer y Analizar Datos**: Obtener información histórica de sensores de forma estructurada
2. **Comparar Periodos**: Facilitar la comparación entre diferentes periodos de cultivo
3. **Exportar Información**: Permitir el uso de datos en herramientas externas
4. **Generar Informes**: Crear documentación para análisis técnico y de negocio

MSAD resuelve estos problemas proporcionando un sistema integrado pero independiente que procesa los datos sin interferir con las operaciones principales del sistema.

## Estructura Simplificada

La nueva versión de MSAD ha sido optimizada con una estructura minimalista:

```
msad/
├── __init__.py           # Importación minimalista
├── api/
│   ├── __init__.py       # Inicialización mínima
│   └── simple_routes.py  # Endpoints RESTful simplificados
└── core/
    ├── __init__.py       # Inicialización mínima
    ├── reports.py        # Generación y gestión de reportes
    └── system.py         # Funciones básicas del sistema
```

## API Reference

### 1. Estado del Servicio

**Endpoint:** `GET /api/msad/status`

**Descripción:** Obtiene el estado actual del servicio MSAD.

**Respuesta:**
```json
{
  "success": true,
  "service": "msad",
  "version": "1.0.0-minimal",
  "status": "running"
}
```

### 2. Crear Datos de Prueba

**Endpoint:** `POST /api/msad/test-data`

**Descripción:** Inserta datos aleatorios para pruebas.

**Cuerpo de la Solicitud:**
```json
{
  "client_id": "mushroom1",
  "count": 20
}
```

**Parámetros:**
- `client_id` (opcional): ID del cliente (por defecto: "mushroom1")
- `count` (opcional): Número de registros a crear (por defecto: 10)

**Respuesta:**
```json
{
  "success": true,
  "message": "Se insertaron 20 registros de prueba para el cliente mushroom1",
  "count": 20
}
```

### 3. Generar Reporte

**Endpoint:** `POST /api/clients/{client_id}/msad/reports`

**Descripción:** Genera un reporte con los datos especificados.

**Cuerpo de la Solicitud:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-05-01",
  "data_type": "sensors",
  "format": "json"
}
```

**Parámetros:**
- `start_date` (obligatorio): Fecha inicial en formato YYYY-MM-DD
- `end_date` (obligatorio): Fecha final en formato YYYY-MM-DD
- `data_type` (opcional): Tipo de datos ("sensors", "events", "actuators")
- `format` (opcional): Formato del archivo ("json", "csv")

**Respuesta Exitosa:**
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

### 4. Listar Reportes de un Cliente

**Endpoint:** `GET /api/clients/{client_id}/msad/reports`

**Descripción:** Lista todos los reportes disponibles para un cliente específico.

**Parámetros de Consulta:**
- `format` (opcional): Filtrar por formato ("json", "csv")
- `data_type` (opcional): Filtrar por tipo de datos ("sensors", "events", "actuators")

**Respuesta:**
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

### 5. Listar Todos los Reportes

**Endpoint:** `GET /api/msad/reports`

**Descripción:** Lista todos los reportes disponibles para todos los clientes.

**Parámetros de Consulta:**
- `format` (opcional): Filtrar por formato ("json", "csv")
- `data_type` (opcional): Filtrar por tipo de datos ("sensors", "events", "actuators")

**Respuesta:** Similar a la del endpoint 4, pero incluyendo reportes de todos los clientes.

### 6. Descargar Reporte

**Endpoint:** `GET /api/clients/{client_id}/msad/reports/download/{filename}`

**Descripción:** Descarga un archivo de reporte específico.

**Parámetros:**
- `client_id`: ID del cliente
- `filename`: Nombre del archivo a descargar

**Respuesta:** Archivo binario con el contenido del reporte.

## Tipos de Datos

Los valores disponibles para el parámetro `data_type` son:

| Valor | Descripción |
|-------|-------------|
| `sensors` | Datos de sensores SHT3x (temperatura y humedad) |
| `events` | Eventos del sistema |
| `actuators` | Acciones de los actuadores |

## Formatos de Reporte

Los valores disponibles para el parámetro `format` son:

| Valor | Descripción |
|-------|-------------|
| `json` | Formato JSON estructurado |
| `csv` | Formato CSV para importación en hojas de cálculo |

## Ejemplos de Uso

### Ejemplo 1: Consulta de Estado
```bash
curl -X GET http://192.168.137.214:5000/api/msad/status
```

### Ejemplo 2: Creación de Reporte
```bash
curl -X POST http://192.168.137.214:5000/api/clients/mushroom1/msad/reports \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01",
    "end_date": "2025-05-01",
    "data_type": "sensors",
    "format": "json"
  }'
```

### Ejemplo 3: Obtener Reportes Filtrados
```bash
curl -X GET "http://192.168.137.214:5000/api/clients/mushroom1/msad/reports?format=json&data_type=sensors"
```

## Instalación

MSAD se integra automáticamente con el servidor Flask principal de RaspServer. No requiere instalación adicional.

## Desarrollo

Para extender la funcionalidad de MSAD, se recomienda:

1. Añadir nuevas funciones en `msad/core/reports.py` para tipos de reportes adicionales
2. Extender `msad/api/simple_routes.py` para añadir nuevos endpoints
3. Mantener la simplicidad y evitar dependencias innecesarias

## Almacenamiento

Los reportes generados se almacenan en la estructura:
```
/mnt/storage/msad/reports/{client_id}/{filename}
```

En sistemas Windows (desarrollo), la ruta equivalente es:
```
RaspServer/storage/msad/reports/{client_id}/{filename}
```

## Solución de Problemas

Si experimentas problemas con los reportes:

1. Verifica que haya datos para el cliente y rango de fechas especificado
2. Asegúrate de usar el formato correcto de fechas (YYYY-MM-DD)
3. Revisa los logs en `/mnt/storage/msad/logs/msad.log`
4. Usa el endpoint `/api/msad/test-data` para generar datos de prueba

## Licencia

Este componente forma parte de RaspServer y está sujeto a la misma licencia del proyecto principal. 