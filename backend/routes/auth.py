from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.validation import validate_registration, validate_login, PASSCODE_REGEX
from backend.utils.security import hash_password, check_password, hash_passcode, check_passcode, login_required
from backend.database.models import UserModel

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    errors, clean_data = validate_registration(data)
    if errors:
        return error_response(errors[0], 400, errors=errors)

    # Check for existing email
    existing = UserModel.get_auth_record(clean_data['email'])
    if existing:
        return error_response("An account with this email already exists.", 409)

    pwd_hash = hash_password(clean_data['password'])
    passcode_hash = hash_passcode(clean_data['passcode'])

    user = UserModel.create(
        name=clean_data['name'],
        email=clean_data['email'],
        password_hash=pwd_hash,
        passcode_hash=passcode_hash
    )

    # Automatically set session on successful registration
    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']

    return success_response(data=user, message="Registration successful.", status_code=201)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    errors, clean_data = validate_login(data)
    if errors:
        return error_response(errors[0], 400, errors=errors)

    user = UserModel.get_auth_record(clean_data['email'])
    if not user or not check_password(user['password_hash'], clean_data['password']):
        return error_response("Invalid email or password.", 401)

    # Start clean session
    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']

    return success_response(
        data={
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        },
        message="Login successful."
    )

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return success_response(message="Logged out successfully.")

@auth_bp.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return error_response("Not authenticated.", 401)

    user = UserModel.get_by_id(user_id)
    if not user:
        session.clear()
        return error_response("User not found.", 404)

    return success_response(data=user)

@auth_bp.route('/passcode', methods=['PUT'])
@login_required
def update_passcode():
    data = request.get_json() or {}
    current_passcode = data.get('current_passcode', '')
    new_passcode = (data.get('new_passcode') or '').strip()

    if not new_passcode or not PASSCODE_REGEX.match(new_passcode):
        return error_response("New passcode must be 4 to 8 digits.", 400)

    user_id = session['user_id']
    record = UserModel.get_private_record(user_id)
    if not record or not check_passcode(record['private_passcode_hash'], current_passcode):
        return error_response("Current private passcode is incorrect.", 403)

    UserModel.update_passcode(user_id, hash_passcode(new_passcode))
    return success_response(message="Private passcode updated successfully.")
