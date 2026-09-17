from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import login_required, check_passcode
from backend.database.models import UserModel

private_bp = Blueprint('private_access', __name__, url_prefix='/api/private-access')

@private_bp.route('/verify', methods=['POST'])
@login_required
def verify_access():
    user_id = session['user_id']
    data = request.get_json() or {}
    passcode = (data.get('passcode') or '').strip()

    if not passcode:
        return error_response("Passcode is required.", 400)

    user_record = UserModel.get_private_record(user_id)
    if not user_record:
        return error_response("User not found.", 404)

    stored_hash = user_record.get('private_passcode_hash')
    if not stored_hash or not check_passcode(stored_hash, passcode):
        return error_response("Incorrect access code.", 401)

    # Set private unlocked flag on the session
    session['private_unlocked'] = True

    return success_response(
        data={"unlocked": True},
        message="Private access verified."
    )

@private_bp.route('/lock', methods=['POST'])
@login_required
def lock_access():
    """Quick exit endpoint: immediately clear private space authorization."""
    session['private_unlocked'] = False
    return success_response(
        data={"unlocked": False},
        message="Private access locked."
    )

@private_bp.route('/status', methods=['GET'])
@login_required
def status():
    """Check if the current session has verified private access."""
    is_unlocked = bool(session.get('private_unlocked'))
    return success_response(data={"unlocked": is_unlocked})
