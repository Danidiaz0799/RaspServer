"""
System routes module for MSAD - Status and general system endpoints
"""
from flask import Blueprint, jsonify, request
from msad.core.system import logger, insert_test_data

def create_system_blueprint():
    """
    Creates and returns a blueprint for system-related endpoints
    """
    system_bp = Blueprint('msad_system_bp', __name__)
    
    @system_bp.route('/msad/status', methods=['GET'])
    def get_status():
        """Endpoint to check service status"""
        return jsonify({
            "success": True,
            "service": "msad",
            "version": "1.1.0",
            "status": "running"
        })
    
    @system_bp.route('/msad/test-data', methods=['POST'])
    def create_test_data():
        """Endpoint to create test data"""
        try:
            data = request.json or {}
            client_id = data.get('client_id', 'mushroom1')
            count = int(data.get('count', 10))
            
            result = insert_test_data(client_id, count)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return system_bp 