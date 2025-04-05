"""
MSAD - Microservicio de Almacenamiento Distribuido (Versión Minimalista)
"""

__version__ = '1.0.0'

# Solo exportamos las funciones que necesitamos para la integración con app.py
from msad.api.simple_routes import create_msad_blueprint, create_export_blueprint
from msad.core.system import init_msad, shutdown_msad

# Estos son usados directamente por app.py
__all__ = [
    'create_msad_blueprint',
    'create_export_blueprint',
    'init_msad',
    'shutdown_msad'
] 