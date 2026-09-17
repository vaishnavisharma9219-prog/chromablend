from pathlib import Path
from flask import Blueprint, request, session, send_file
from backend.utils.responses import success_response, error_response
from backend.utils.security import private_access_required
from backend.services.document_service import save_document, delete_document
from backend.database.models import DocumentModel

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

STANDARD_CHECKLIST = [
    {"key": "gov_id", "label": "Government ID / Passport scan"},
    {"key": "emergency_contacts", "label": "Emergency contacts printed / written card"},
    {"key": "medical_info", "label": "Prescriptions & critical medical documentation"},
    {"key": "financial_records", "label": "Bank account & payment backup records"},
    {"key": "housing_legal", "label": "Lease, legal documents, or custody paperwork"}
]

@documents_bp.route('', methods=['GET'])
@private_access_required
def get_documents():
    user_id = session['user_id']
    category = request.args.get('category')
    docs = DocumentModel.get_all(user_id, category=category)
    return success_response(data=docs)

@documents_bp.route('', methods=['POST'])
@private_access_required
def upload_document():
    user_id = session['user_id']
    if 'file' not in request.files:
        return error_response("No file provided in form data.", 400)

    file = request.files['file']
    category = request.form.get('category', 'Other').strip()

    try:
        doc = save_document(user_id=user_id, file_storage=file, category=category)
        return success_response(data=doc, message="File uploaded to vault.", status_code=201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", 500)

@documents_bp.route('/<int:doc_id>/download', methods=['GET'])
@private_access_required
def download_document(doc_id):
    user_id = session['user_id']
    doc = DocumentModel.get_by_id(doc_id, user_id)
    if not doc:
        return error_response("Document not found or unauthorized.", 404)

    file_path = Path(doc['file_path'])
    if not file_path.exists():
        return error_response("The document file was not found on server storage.", 404)

    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=doc['original_filename'],
        mimetype=doc.get('mime_type') or 'application/octet-stream'
    )

@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@private_access_required
def remove_document(doc_id):
    user_id = session['user_id']
    deleted = delete_document(user_id, doc_id)
    if not deleted:
        return error_response("Document not found or unauthorized.", 404)
    return success_response(message="Document removed from vault.")

@documents_bp.route('/checklist', methods=['GET'])
@private_access_required
def get_checklist():
    user_id = session['user_id']
    user_state = DocumentModel.get_checklists(user_id)
    
    # Merge with standard items
    items = []
    for item in STANDARD_CHECKLIST:
        items.append({
            "key": item["key"],
            "label": item["label"],
            "is_checked": user_state.get(item["key"], False)
        })
    return success_response(data=items)

@documents_bp.route('/checklist', methods=['POST'])
@private_access_required
def toggle_checklist():
    user_id = session['user_id']
    data = request.get_json() or {}
    item_key = (data.get('item_key') or '').strip()
    is_checked = bool(data.get('is_checked', False))

    if not item_key:
        return error_response("item_key is required.", 400)

    DocumentModel.set_checklist_item(user_id, item_key, is_checked)
    return success_response(message="Checklist item updated.")
