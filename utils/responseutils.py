from flask import jsonify

def api_response(success, message=None, data=None, status_code=200):
    """
    Standardized API response format
    
    Args:
        success: Boolean indicating success/failure
        message: Optional message string
        data: Optional data dictionary
        status_code: HTTP status code
        
    Returns:
        tuple: (Flask response object, status_code)
    """
    response = {'success': success}
    if message:
        response['message'] = message
    if data:
        response.update(data)
    return jsonify(response), status_code
