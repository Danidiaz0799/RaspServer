# 🍄 RaspMush: Sistema de Monitoreo y Control para Cultivo de Orellana Rosada

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Estado](https://img.shields.io/badge/estado-activo-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-orange)

## 📋 Contenido
- [Planteamiento del Problema](#planteamiento-del-problema)
- [Objetivos](#objetivos)
- [Arquitectura](#arquitectura)
- [Modos de Operación](#modos-de-operación)
- [Comunicación MQTT](#comunicación-mqtt)
- [Respaldo con MSAD](#respaldo-con-msad)
- [Configuración para Orellana Rosada](#configuración-para-orellana-rosada)
- [API REST](#api-rest)
- [Base de Datos](#base-de-datos)
- [Guía de Desarrollo](#guía-de-desarrollo)

> **NOTA**: Para instrucciones de instalación y configuración, consulte [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

## 📝 Planteamiento del Problema

El cultivo de setas Orellana Rosada en entornos controlados se enfrenta a desafíos significativos debido a la falta de integración de soluciones a medida para sistemas de monitoreo adecuados de las condiciones ambientales en procesos de agricultura distribuida. Actualmente, los fungicultores dependen de sistemas manuales para gestionar variables cruciales como la temperatura, la humedad y el CO₂, lo que genera inconsistencias que resultan en:

- Baja productividad y rendimiento
- Pérdida de calidad del producto final
- Desperdicio de recursos e insumos
- Limitaciones para escalar la producción

Si bien las tecnologías basadas en IoT representan una solución prometedora para optimizar el control ambiental y mejorar la eficiencia operativa, el alto costo de implementación, junto con la falta de conocimientos técnicos y soporte adecuado, especialmente en zonas rurales, han dificultado su adopción entre pequeños productores. Esto ha afectado negativamente la competitividad del cultivo y ha limitado la capacidad de maximizar el rendimiento y minimizar los costos operativos, comprometiendo la sostenibilidad del sistema de cultivo de setas Orellana Rosada.

## 🎯 Objetivos

### Objetivo General
Desarrollar una red de monitoreo y control ambiental que permita la gestión centralizada de múltiples cultivos de setas Orellana Rosada mediante un sistema de servidor local con MSAD (Microservicio de Almacenamiento Distribuido).

### Objetivos Específicos
1. **Implementar sistema MQTT para gestión múltiple**: Desarrollar una red de comunicación basada en MQTT que permita la interconexión entre múltiples nodos de cultivo y el servidor central, facilitando tanto el control manual como automático de cada unidad de producción.

2. **Desarrollar dual control manual/automático**: Crear un sistema flexible que permita al cultivador elegir entre modo automático (basado en parámetros predefinidos para Orellana Rosada) o modo manual (con control directo sobre actuadores) para cada cultivo de forma independiente.

3. **Centralizar monitoreo con interfaz unificada**: Implementar un panel de control que muestre en tiempo real el estado de todos los cultivos, permitiendo la supervisión simultánea y la alternancia entre modos operativos según las necesidades de cada fase de crecimiento.

4. **Garantizar persistencia mediante MSAD**: Desarrollar un sistema de respaldo local que asegure la integridad de los datos de cultivo y configuraciones, incluso en entornos rurales con conectividad limitada o inexistente.

## 🏗️ Arquitectura

RaspMush implementa una arquitectura distribuida optimizada para el cultivo de Orellana Rosada, con los siguientes componentes:

```
┌─────────────────────────────────────────────────────────────────┐
│                        RaspMush Server                          │
├────────────┬─────────────┬─────────────────┬──────────────────┐ │
│ Servidor   │ Broker MQTT │ Base de Datos   │ MSAD             │ │
│ Web (Flask)│ (Mosquitto) │ (SQLite)        │ (Almacenamiento) │ │
├────────────┴─────────────┴─────────────────┴──────────────────┤ │
│                          API REST                              │ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
       ┌───────────────────┐│┌───────────────────┐  ┌───────────────────┐
       │  Nodo Cultivo #1  │││  Nodo Cultivo #2  │  │  Nodo Cultivo #N  │
       │  (Raspberry Pi)   │││  (ESP32)          │  │  (Arduino)        │
       ├───────────────────┤││├───────────────────┤  ├───────────────────┤
       │ ┌───────┐ ┌─────┐ │││ ┌───────┐ ┌─────┐ │  │ ┌───────┐ ┌─────┐ │
       │ │SHT3X  │ │Venti-│││ │SHT3X  │ │Venti-│ │  │ │SHT3X  │ │Venti-│ │
       │ │CO₂    │ │lación│││ │CO₂    │ │lación│ │  │ │CO₂    │ │lación│ │
       │ └───────┘ └─────┘ │││ └───────┘ └─────┘ │  │ └───────┘ └─────┘ │
       └───────────────────┘││└───────────────────┘  └───────────────────┘
                           ││
```

### Componentes Principales:

1. **Servidor Central**: 
   - Gestiona la comunicación entre nodos
   - Procesa y almacena datos de cultivos
   - Ejecuta algoritmos de control para Orellana Rosada
   - Sirve la interfaz web para monitoreo y control

2. **Nodos de Cultivo**:
   - Desplegados en cada zona de cultivo
   - Equipados con sensores específicos (temperatura, humedad, CO₂)
   - Controlan actuadores locales (ventilación, humidificación, iluminación)
   - Se comunican con el servidor mediante MQTT

3. **Sistema MSAD**:
   - Proporciona almacenamiento distribuido
   - Garantiza la persistencia de datos históricos
   - Facilita la recuperación ante fallos
   - Opera localmente sin dependencia de internet

## 🔄 Modos de Operación

RaspMush permite controlar cada cultivo de forma independiente en dos modos operativos:

### Modo Automático
En modo automático, el sistema controla los actuadores según parámetros predefinidos:

- **Funcionalidades**:
  - Control on/off basado en umbrales de temperatura y humedad
  - Operación según fase de cultivo actual (incubación, inducción, fructificación)
  - Registro continuo de condiciones y acciones realizadas

- **Ventajas**:
  - Operación continua sin intervención manual
  - Decisiones basadas en parámetros predefinidos
  - Mantenimiento de condiciones según la fase de cultivo

### Modo Manual
El modo manual permite al cultivador tomar el control directo:

- **Funcionalidades**:
  - Control directo de ventilación, humidificación e iluminación
  - Monitoreo continuo mientras se mantiene el control manual
  - Cambio de fase de cultivo según criterio del operador

- **Ventajas**:
  - Control total durante etapas críticas del cultivo
  - Respuesta inmediata a condiciones imprevistas
  - Flexibilidad para ajustes específicos

### Cambio de Modo
El cambio entre modos se puede realizar desde:
- Panel de control principal
- API REST
- Mensajes MQTT específicos

```json
// Ejemplo de cambio de modo a través de MQTT
// Topic: cultivos/orellana1/modo
{
  "modo": "automatico",      // o "manual"
  "fase": "fructificacion",  // solo si es automatico
  "timestamp": "2023-05-15T08:30:00Z"
}
```

## 📡 Comunicación MQTT

RaspMush utiliza una estructura jerárquica de tópicos MQTT:

```
cultivos/{cultivo_id}/
  ├── registro                # Registro del nodo de cultivo
  ├── estado/
  │   ├── online              # Estado de conexión del nodo
  │   ├── fase                # Fase actual del cultivo
  │   └── alertas             # Notificaciones de condiciones anómalas
  ├── modo                    # Modo de operación (manual/automático)
  ├── sensores/
  │   ├── sht3x               # Datos de temperatura y humedad
  │   ├── co2                 # Niveles de CO₂
  │   └── luz                 # Intensidad lumínica
  └── actuadores/
      ├── ventilacion         # Control de ventiladores
      ├── humidificador       # Control del sistema de humidificación
      ├── iluminacion         # Control de ciclos de luz
      └── calefactor          # Control de temperatura
```

### Formato de Mensajes

Los mensajes MQTT utilizan JSON:

#### 1. Registro de Cultivo
```json
// Topic: cultivos/orellana1/registro
{
  "cultivo_id": "orellana1",
  "nombre": "Cultivo Orellana Rosada 1",
  "ubicacion": "Nave principal",
  "especie": "Pleurotus djamor",
  "fase_actual": "incubacion",
  "modo": "automatico",
  "sensores": ["sht3x", "co2"],
  "actuadores": ["ventilacion", "humidificador", "iluminacion"]
}
```

#### 2. Datos de Sensores SHT3X
```json
// Topic: cultivos/orellana1/sensores/sht3x
{
  "temperatura": 24.5,
  "humedad": 85.3,
  "timestamp": "2023-04-03T14:22:16Z",
  "fase": "incubacion",
  "modo": "automatico"
}
```

#### 3. Control de Ventilación
```json
// Topic: cultivos/orellana1/actuadores/ventilacion
{
  "estado": 1,           // 0 = apagado, 1 = encendido
  "intensidad": 75,      // Intensidad (0-100)
  "automatico": true,    // ¿Control automático?
  "timestamp": "2023-04-03T14:22:16Z"
}
```

## 🔄 Respaldo con MSAD

El sistema MSAD (Microservicio de Almacenamiento Distribuido) garantiza la integridad de los datos de cultivo:

### Características Implementadas:

1. **Respaldo Automático**:
   - Respaldos diarios de la base de datos
   - Copias de seguridad semanales y mensuales
   - Rotación automática de archivos antiguos

2. **Recuperación de Datos**:
   - Restauración de base de datos desde copias
   - Opciones para recuperación completa o parcial

3. **Exportación de Datos**:
   - Exportación en formatos CSV/JSON para análisis
   - Generación de informes de cultivo

4. **Operación Local**:
   - Funcionamiento sin conexión a internet
   - Almacenamiento en la red local

## 🍄 Configuración para Orellana Rosada

RaspMush incluye configuraciones optimizadas para el cultivo de Pleurotus djamor (Orellana Rosada):

### Parámetros Óptimos por Fase
| Fase | Temperatura | Humedad | Luz | CO₂ | Duración |
|------|-------------|---------|-----|-----|----------|
| Incubación | 24-28°C | 85-90% | 0h | Alto | 10-14 días |
| Inducción | 22-24°C | 90-95% | 8h | Bajo | 2-3 días |
| Fructificación | 22-26°C | 80-90% | 10h | Bajo | 7-14 días |

### Control Automatizado
- **Temperatura**: Control on/off basado en umbrales
- **Humedad**: Activación/desactivación según mediciones
- **Iluminación**: Ciclos diarios según fase

## 🔌 API REST

RaspMush proporciona una API REST para interactuar con el sistema:

### Endpoints Principales

| Endpoint | Método | Descripción | Ejemplo de Respuesta |
|----------|--------|-------------|----------------------|
| `/api/status` | GET | Estado del servidor | `{"status": "ok", "uptime": 3600, "version": "1.0.0"}` |
| `/api/cultivos` | GET | Lista de cultivos | `[{"cultivo_id": "orellana1", "nombre": "Cultivo 1", "estado": "online", "fase": "fructificacion", "modo": "automatico"}]` |
| `/api/cultivos/{cultivo_id}` | GET | Información de cultivo | `{"cultivo_id": "orellana1", "nombre": "Cultivo 1", "ubicacion": "Nave A", "fase": "fructificacion", "modo": "automatico", "inicio_fase": "2023-07-10", "sensores": [...], "actuadores": [...]}` |
| `/api/cultivos/{cultivo_id}/modo` | PUT | Cambiar modo de operación | Payload: `{"modo": "manual"}` o `{"modo": "automatico", "fase": "fructificacion"}` |
| `/api/cultivos/{cultivo_id}/sensores/{sensor_id}` | GET | Datos de sensor | `{"temperatura": 24.5, "humedad": 85.2, "timestamp": "2023-07-15T14:23:45Z"}` |
| `/api/cultivos/{cultivo_id}/actuadores/{actuador_id}` | POST | Controlar actuador | Payload: `{"estado": 1, "intensidad": 75}` |
| `/api/cultivos/{cultivo_id}/fases` | PUT | Cambiar fase de cultivo | Payload: `{"fase": "fructificacion", "fecha_inicio": "2023-07-15"}` |
| `/api/cultivos/{cultivo_id}/reportes/rendimiento` | GET | Reporte de rendimiento | `{"ciclo_actual": 3, "produccion_estimada": "12kg", "eficiencia_biologica": "85%"}` |

## 💾 Base de Datos

El esquema de la base de datos para el seguimiento de cultivos:

### Tablas Principales

#### 1. Cultivos
```sql
CREATE TABLE cultivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cultivo_id TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    especie TEXT DEFAULT 'Pleurotus djamor',
    fase_actual TEXT,
    modo_operacion TEXT DEFAULT 'automatico',
    fecha_inicio_fase DATE,
    ciclo_numero INTEGER DEFAULT 1,
    estado TEXT DEFAULT 'offline',
    ultima_conexion TIMESTAMP,
    ip_address TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Datos de Sensores
```sql
CREATE TABLE datos_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cultivo_id TEXT NOT NULL,
    sensor_tipo TEXT NOT NULL,
    temperatura REAL,
    humedad REAL,
    co2_nivel REAL,
    luz_nivel REAL,
    fase_cultivo TEXT,
    modo_operacion TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cultivo_id) REFERENCES cultivos(cultivo_id) ON DELETE CASCADE
);
```

#### 3. Configuración de Fases
```sql
CREATE TABLE config_fases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cultivo_id TEXT NOT NULL,
    fase TEXT NOT NULL,
    temp_min REAL,
    temp_max REAL,
    humedad_min REAL,
    humedad_max REAL,
    co2_max REAL,
    luz_horas INTEGER,
    ventilacion_frecuencia INTEGER,
    ventilacion_duracion INTEGER,
    UNIQUE(cultivo_id, fase),
    FOREIGN KEY (cultivo_id) REFERENCES cultivos(cultivo_id) ON DELETE CASCADE
);
```

## 🧩 Guía de Desarrollo

### Implementación de Cambio de Modo

Para cambiar el modo de operación de un cultivo:

```python
def cambiar_modo_cultivo(cultivo_id, modo, fase=None):
    """
    Cambia el modo de operación de un cultivo (manual/automático)
    
    :param cultivo_id: ID del cultivo
    :param modo: 'manual' o 'automatico'
    :param fase: Fase del cultivo (requerido si modo='automatico')
    :return: True si se realizó el cambio, False en caso contrario
    """
    if modo not in ['manual', 'automatico']:
        print(f"Modo no válido: {modo}")
        return False
        
    if modo == 'automatico' and fase is None:
        print("Debe especificar una fase para el modo automático")
        return False
    
    # Actualizar en base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if modo == 'automatico':
        cursor.execute(
            "UPDATE cultivos SET modo_operacion = ?, fase_actual = ? WHERE cultivo_id = ?",
            (modo, fase, cultivo_id)
        )
    else:
        cursor.execute(
            "UPDATE cultivos SET modo_operacion = ? WHERE cultivo_id = ?",
            (modo, cultivo_id)
        )
    
    conn.commit()
    conn.close()
    
    # Publicar cambio en MQTT
    payload = {
        "modo": modo,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    if modo == 'automatico':
        payload["fase"] = fase
    
    mqtt_client.publish(f"cultivos/{cultivo_id}/modo", json.dumps(payload))
    
    print(f"Cultivo {cultivo_id} cambiado a modo {modo}")
    return True
```

### Implementación en Nodos para Responder a Cambios de Modo

```python
# En el callback de mensajes MQTT del nodo
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    
    # Procesar cambio de modo
    if topic == f"cultivos/{CULTIVO_ID}/modo":
        modo = payload.get("modo")
        if modo == "automatico":
            fase = payload.get("fase")
            print(f"Cambiando a modo automático, fase: {fase}")
            activar_modo_automatico(fase)
        elif modo == "manual":
            print("Cambiando a modo manual")
            activar_modo_manual()
```

---

<div align="center">
  <p>RaspMush: Solución integral para el cultivo profesional de setas Orellana Rosada</p>
  <p>Para instrucciones de instalación, consulte <a href="INSTALLATION_GUIDE.md">INSTALLATION_GUIDE.md</a></p>
</div>
