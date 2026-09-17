from functools import wraps
from flask import session, request
from werkzeug.security import generate_password_hash, check_password_hash
from backend.utils.responses import error_response

def hash_password(password: str) -> str:
    """Hash a plaintext password using Werkzeug."""
    return generate_password_hash(password)

def check_password(password_hash: str, password: str) -> bool:
    """Verify a password against its stored hash."""
    if not password_hash or not password:
        return False
    return check_password_hash(password_hash, password)

def hash_passcode(passcode: str) -> str:
    """Hash a private numeric passcode."""
    return generate_password_hash(passcode)

def check_passcode(passcode_hash: str, passcode: str) -> bool:
    """Verify a private passcode against its stored hash."""
    if not passcode_hash or not passcode:
        return False
    return check_password_hash(passcode_hash, passcode)

def login_required(f):
    """Decorator to require an authenticated session for user-specific endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return error_response("Authentication required. Please log in.", 401)
        return f(*args, **kwargs)
    return decorated_function

def private_access_required(f):
    """Decorator to require that the user has verified their private access passcode."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return error_response("Authentication required. Please log in.", 401)
        if not session.get('private_unlocked'):
            return error_response("Private access verification required.", 403)
        return f(*args, **kwargs)
    return decorated_function
