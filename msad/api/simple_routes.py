"""
Rutas simplificadas para MSAD
"""
from flask import Blueprint, jsonify, request, send_file
import os

from msad.core.system import logger, insert_test_data
from msad.core.reports import generate_report, list_reports, get_report_file

def create_msad_blueprint():
    """
    Crea y devuelve un blueprint minimalista para la integración con Flask
    """
    msad_bp = Blueprint('msad_bp', __name__)
    
    @msad_bp.route('/msad/status', methods=['GET'])
    def get_status():
        """Endpoint para verificar el estado del servicio"""
        return jsonify({
            "success": True,
            "service": "msad",
            "version": "1.0.0-minimal",
            "status": "running"
        })
    
    @msad_bp.route('/msad/test-data', methods=['POST'])
    def create_test_data():
        """Endpoint para crear datos de prueba"""
        try:
            data = request.json or {}
            client_id = data.get('client_id', 'mushroom1')
            count = int(data.get('count', 10))
            
            result = insert_test_data(client_id, count)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error al crear datos de prueba: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return msad_bp

def create_export_blueprint():
    """
    Crea y devuelve un blueprint para gestión de reportes
    """
    reports_bp = Blueprint('reports_bp', __name__)
    
    # 1. Endpoint para crear un reporte
    @reports_bp.route('/clients/<client_id>/msad/reports', methods=['POST'])
    def create_report(client_id):
        """Endpoint para crear un reporte de datos"""
        try:
            # Obtener parámetros de la solicitud
            data = request.json
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Se requiere un cuerpo JSON en la solicitud"
                }), 400
                
            # Extraer parámetros
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            data_type = data.get('data_type', 'sensors')
            format = data.get('format', 'json')
            
            # Validar parámetros obligatorios
            if not start_date or not end_date:
                return jsonify({
                    "success": False,
                    "error": "Se requiere start_date y end_date"
                }), 400
                
            # Generar reporte
            result = generate_report(client_id, start_date, end_date, data_type, format)
            
            # Determinar el código de respuesta
            if result.get('success', False):
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Error al crear reporte: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    # 2. Endpoint para listar reportes
    @reports_bp.route('/clients/<client_id>/msad/reports', methods=['GET'])
    def get_client_reports(client_id):
        """Endpoint para listar reportes de un cliente"""
        try:
            # Obtener parámetros de filtrado opcionales
            format = request.args.get('format')
            data_type = request.args.get('data_type')
            
            # Listar reportes
            result = list_reports(client_id, format, data_type)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error al listar reportes: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    # 3. Endpoint para listar todos los reportes
    @reports_bp.route('/msad/reports', methods=['GET'])
    def get_all_reports():
        """Endpoint para listar todos los reportes"""
        try:
            # Obtener parámetros de filtrado opcionales
            format = request.args.get('format')
            data_type = request.args.get('data_type')
            
            # Listar reportes
            result = list_reports(None, format, data_type)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error al listar reportes: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    # 4. Endpoint para descargar un reporte
    @reports_bp.route('/clients/<client_id>/msad/reports/download/<filename>', methods=['GET'])
    def download_report(client_id, filename):
        """Endpoint para descargar un reporte"""
        try:
            # Obtener la ruta del archivo
            file_path = get_report_file(client_id, filename)
            
            if not file_path:
                return jsonify({
                    "success": False,
                    "error": "Archivo no encontrado"
                }), 404
                
            # Determinar tipo MIME según la extensión
            mime_type = "application/octet-stream"  # Valor por defecto
            
            if filename.endswith('.json'):
                mime_type = "application/json"
            elif filename.endswith('.csv'):
                mime_type = "text/csv"
                
            # Enviar el archivo
            return send_file(
                file_path,
                mimetype=mime_type,
                as_attachment=True,
                download_name=filename
            )
                
        except Exception as e:
            logger.error(f"Error al descargar reporte: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    return reports_bp 