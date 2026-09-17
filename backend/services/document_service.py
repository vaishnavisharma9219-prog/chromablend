import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
from backend.database.models import DocumentModel

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is permitted."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'txt', 'docx', 'doc', 'csv'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_document(user_id: int, file_storage, category: str):
    """
    Save an uploaded file safely to the upload directory and create a database record.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file was selected for upload.")

    original_filename = secure_filename(file_storage.filename)
    if not original_filename:
        original_filename = "document"

    if not is_allowed_file(original_filename):
        raise ValueError("Unsupported file type. Allowed formats: PDF, PNG, JPG, WEBP, TXT, DOCX, CSV.")

    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'bin'
    stored_filename = f"user_{user_id}_{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination_path = upload_dir / stored_filename

    # Save file to disk
    file_storage.save(destination_path)
    file_size = destination_path.stat().st_size
    mime_type = file_storage.content_type or 'application/octet-stream'

    # Save metadata in SQLite
    doc_record = DocumentModel.create(
        user_id=user_id,
        category=category or 'Other',
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(destination_path),
        file_size=file_size,
        mime_type=mime_type
    )
    return doc_record

def delete_document(user_id: int, doc_id: int) -> bool:
    """
    Verify ownership and delete document from both disk and database.
    """
    doc = DocumentModel.get_by_id(doc_id, user_id)
    if not doc:
        return False

    file_path = Path(doc['file_path'])
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        current_app.logger.error(f"Failed to delete file from disk: {e}")

    # Remove database record
    return DocumentModel.delete(doc_id, user_id)
