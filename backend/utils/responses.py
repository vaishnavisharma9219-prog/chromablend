from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """Format and return a standardized success JSON response."""
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(payload), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    """Format and return a standardized error JSON response."""
    payload = {
        "success": False,
        "error": message
    }
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code
