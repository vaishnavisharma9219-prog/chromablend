import re
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PASSCODE_REGEX = re.compile(r'^\d{4,8}$')

def validate_registration(data):
    """Validate user registration payload."""
    errors = []
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    passcode = (data.get('passcode') or '1984').strip()

    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters long.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email address is required.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")
    if passcode and not PASSCODE_REGEX.match(passcode):
        errors.append("Private passcode must be 4 to 8 digits.")

    return errors, {
        'name': name,
        'email': email,
        'password': password,
        'passcode': passcode or '1984'
    }

def validate_login(data):
    """Validate user login payload."""
    errors = []
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email:
        errors.append("Email is required.")
    if not password:
        errors.append("Password is required.")

    return errors, {'email': email, 'password': password}

def validate_date(date_str):
    """Ensure date is in YYYY-MM-DD format."""
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
