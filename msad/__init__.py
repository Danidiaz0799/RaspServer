"""
MSAD - Microservicio de Almacenamiento Distribuido
"""

__version__ = '1.0.0'

# Importar todo desde el módulo principal
from msad.msad_main import *

# Importar y exponer funciones principales para mantener compatibilidad
from msad.core.system_utils import init_msad, shutdown_msad, get_msad_status
from msad.core.backup_manager import create_backup
from msad.server.web_server import MSADServer
from msad.config import ensure_directories, get_storage_path, get_database_path
from msad.api.flask_routes import create_msad_blueprint

# Inicializar módulo automáticamente
from msad.core.system_utils import init
init() 