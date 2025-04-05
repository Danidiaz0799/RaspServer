"""
Rutas y endpoints para la integración de MSAD con Flask
"""
from flask import Blueprint, jsonify, request

from msad.core.system_utils import init_msad, shutdown_msad, get_msad_status
from msad.core.backup_manager import create_backup

def create_msad_blueprint():
    """
    Crea y devuelve un blueprint de Flask para las rutas de MSAD.
    """
    # Blueprint para las rutas de MSAD
    msad_bp = Blueprint('msad_bp', __name__)
    
    # Obtener estado del servicio MSAD
    @msad_bp.route('/msad/status', methods=['GET'])
    def get_status():
        result = get_msad_status()
        return jsonify(result)
    
    # Crear un respaldo manual
    @msad_bp.route('/msad/backup', methods=['POST'])
    def backup():
        result = create_backup()
        return jsonify(result)
    
    # Reiniciar el servicio MSAD
    @msad_bp.route('/msad/restart', methods=['POST'])
    def restart():
        shutdown_msad()
        result = init_msad(auto_backup=True, backup_interval_hours=24)
        return jsonify(result)
    
    # Endpoints para integración con el módulo de estadísticas
    @msad_bp.route('/clients/<client_id>/msad/stats', methods=['GET'])
    def get_msad_client_stats(client_id):
        # Obtener estadísticas de MSAD específicas del cliente
        # (En este caso, usamos las estadísticas generales ya que MSAD es un servicio general)
        result = get_msad_status()
        
        # Filtrar solo la información relevante para el cliente
        if result.get('success', False):
            return jsonify({
                "success": True,
                "backups": result.get('backups', {}),
                "server": result.get('server', {})
            })
        
        return jsonify(result)
    
    return msad_bp 