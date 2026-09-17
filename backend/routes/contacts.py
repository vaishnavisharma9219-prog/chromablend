from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import private_access_required
from backend.database.models import ContactModel

contacts_bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')

@contacts_bp.route('', methods=['GET'])
@private_access_required
def get_contacts():
    user_id = session['user_id']
    contacts = ContactModel.get_all(user_id)
    return success_response(data=contacts)

@contacts_bp.route('', methods=['POST'])
@private_access_required
def create_contact():
    user_id = session['user_id']
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()

    if not name or not phone:
        return error_response("Name and phone number are required.", 400)

    relationship = (data.get('relationship') or '').strip()
    notes = (data.get('notes') or '').strip()
    is_primary = 1 if data.get('is_primary') else 0

    contact = ContactModel.create(
        user_id=user_id,
        name=name,
        phone=phone,
        relationship=relationship,
        notes=notes,
        is_primary=is_primary
    )
    return success_response(data=contact, message="Trusted contact added.", status_code=201)

@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@private_access_required
def get_contact(contact_id):
    user_id = session['user_id']
    contact = ContactModel.get_by_id(contact_id, user_id)
    if not contact:
        return error_response("Contact not found.", 404)
    return success_response(data=contact)

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@private_access_required
def update_contact(contact_id):
    user_id = session['user_id']
    existing = ContactModel.get_by_id(contact_id, user_id)
    if not existing:
        return error_response("Contact not found.", 404)

    data = request.get_json() or {}
    name = (data.get('name') or existing['name']).strip()
    phone = (data.get('phone') or existing['phone']).strip()

    if not name or not phone:
        return error_response("Name and phone number cannot be empty.", 400)

    relationship = data.get('relationship', existing['relationship'])
    notes = data.get('notes', existing['notes'])
    is_primary = 1 if data.get('is_primary', existing['is_primary']) else 0

    updated = ContactModel.update(
        contact_id=contact_id,
        user_id=user_id,
        name=name,
        phone=phone,
        relationship=relationship,
        notes=notes,
        is_primary=is_primary
    )
    return success_response(data=updated, message="Contact updated.")

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@private_access_required
def delete_contact(contact_id):
    user_id = session['user_id']
    deleted = ContactModel.delete(contact_id, user_id)
    if not deleted:
        return error_response("Contact not found.", 404)
    return success_response(message="Contact removed.")
