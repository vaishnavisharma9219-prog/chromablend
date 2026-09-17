from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import private_access_required
from backend.services.emergency_service import trigger_sos
from backend.database.models import EmergencyModel

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

@emergency_bp.route('/sos', methods=['POST'])
@private_access_required
def sos_trigger():
    user_id = session['user_id']
    data = request.get_json() or {}
    notes = (data.get('notes') or '').strip()

    status_data = trigger_sos(user_id=user_id, notes=notes)
    return success_response(
        data=status_data,
        message="Emergency SOS recorded.",
        status_code=201
    )

@emergency_bp.route('/history', methods=['GET'])
@private_access_required
def sos_history():
    user_id = session['user_id']
    history = EmergencyModel.get_history(user_id)
    return success_response(data=history)
