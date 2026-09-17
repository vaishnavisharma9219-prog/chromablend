from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import login_required
from backend.database.models import NoteModel

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

@notes_bp.route('', methods=['GET'])
@login_required
def get_notes():
    user_id = session['user_id']
    search = request.args.get('search')
    notes = NoteModel.get_all(user_id, search=search)
    return success_response(data=notes)

@notes_bp.route('', methods=['POST'])
@login_required
def create_note():
    user_id = session['user_id']
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()

    if not title:
        return error_response("Note title is required.", 400)

    content = data.get('content') or ''
    color_tag = data.get('color_tag') or 'charcoal'

    note = NoteModel.create(
        user_id=user_id,
        title=title,
        content=content,
        color_tag=color_tag
    )
    return success_response(data=note, message="Note created.", status_code=201)

@notes_bp.route('/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    user_id = session['user_id']
    note = NoteModel.get_by_id(note_id, user_id)
    if not note:
        return error_response("Note not found.", 404)
    return success_response(data=note)

@notes_bp.route('/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    user_id = session['user_id']
    existing = NoteModel.get_by_id(note_id, user_id)
    if not existing:
        return error_response("Note not found.", 404)

    data = request.get_json() or {}
    title = (data.get('title') or existing['title']).strip()
    if not title:
        return error_response("Note title cannot be empty.", 400)

    content = data.get('content', existing['content'])
    color_tag = data.get('color_tag', existing['color_tag'])

    updated = NoteModel.update(
        note_id=note_id,
        user_id=user_id,
        title=title,
        content=content,
        color_tag=color_tag
    )
    return success_response(data=updated, message="Note updated.")

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    user_id = session['user_id']
    deleted = NoteModel.delete(note_id, user_id)
    if not deleted:
        return error_response("Note not found.", 404)
    return success_response(message="Note deleted successfully.")
