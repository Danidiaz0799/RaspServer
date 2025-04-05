"""
Report routes module for MSAD - Data reporting and export endpoints
"""
from flask import Blueprint, jsonify, request, send_file
from msad.core.system import logger
from msad.core.reports import generate_report, list_reports, get_report_file

def create_report_blueprint():
    """
    Creates and returns a blueprint for report-related endpoints
    """
    report_bp = Blueprint('msad_report_bp', __name__)
    
    @report_bp.route('/clients/<client_id>/msad/reports', methods=['POST'])
    def create_report(client_id):
        """Endpoint to create a data report"""
        try:
            # Get request parameters
            data = request.json
            if not data:
                return jsonify({
                    "success": False,
                    "error": "JSON body required in the request"
                }), 400
                
            # Extract parameters
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            data_type = data.get('data_type', 'sensors')
            format = data.get('format', 'json')
            
            # Validate required parameters
            if not start_date or not end_date:
                return jsonify({
                    "success": False,
                    "error": "start_date and end_date are required"
                }), 400
                
            # Generate report
            result = generate_report(client_id, start_date, end_date, data_type, format)
            
            # Determine response code
            if result.get('success', False):
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    @report_bp.route('/clients/<client_id>/msad/reports', methods=['GET'])
    def get_client_reports(client_id):
        """Endpoint to list reports for a client"""
        try:
            # Get optional filtering parameters
            format = request.args.get('format')
            data_type = request.args.get('data_type')
            
            # List reports
            result = list_reports(client_id, format, data_type)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error listing reports: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    @report_bp.route('/msad/reports', methods=['GET'])
    def get_all_reports():
        """Endpoint to list all reports"""
        try:
            # Get optional filtering parameters
            format = request.args.get('format')
            data_type = request.args.get('data_type')
            
            # List reports
            result = list_reports(None, format, data_type)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error listing reports: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    @report_bp.route('/clients/<client_id>/msad/reports/download/<filename>', methods=['GET'])
    def download_report(client_id, filename):
        """Endpoint to download a report"""
        try:
            # Get file path
            file_path = get_report_file(client_id, filename)
            
            if not file_path:
                return jsonify({
                    "success": False,
                    "error": "File not found"
                }), 404
                
            # Determine MIME type based on extension
            mime_type = "application/octet-stream"  # Default value
            
            if filename.endswith('.json'):
                mime_type = "application/json"
            elif filename.endswith('.csv'):
                mime_type = "text/csv"
                
            # Send file
            return send_file(
                file_path,
                mimetype=mime_type,
                as_attachment=True,
                download_name=filename
            )
                
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    return report_bp 