"""
Punto de entrada principal para el módulo MSAD
"""

__version__ = '1.0.0'

# Importar y exponer funciones principales para mantener compatibilidad
from msad.core.core_exports import (
    init_msad, 
    shutdown_msad, 
    get_msad_status,
    create_backup,
    init
)
from msad.server.server_exports import MSADServer
from msad.config.config_exports import ensure_directories, get_storage_path, get_database_path
from msad.api.api_exports import create_msad_blueprint

# Inicializar módulo automáticamente al importar
init() 