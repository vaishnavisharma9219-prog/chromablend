from datetime import date
from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import login_required
from backend.utils.validation import validate_date
from backend.database.models import PlannerModel

planner_bp = Blueprint('planner', __name__, url_prefix='/api/planner')

VALID_SECTIONS = {'morning', 'afternoon', 'evening'}

@planner_bp.route('', methods=['GET'])
@login_required
def get_planner():
    user_id = session['user_id']
    query_date = request.args.get('date') or date.today().isoformat()

    if not validate_date(query_date):
        return error_response("Date must be in YYYY-MM-DD format.", 400)

    entries = PlannerModel.get_for_date(user_id, query_date)
    
    # Organize by section for easy client consumption
    structured = {
        "date": query_date,
        "morning": [e for e in entries if e['section'] == 'morning'],
        "afternoon": [e for e in entries if e['section'] == 'afternoon'],
        "evening": [e for e in entries if e['section'] == 'evening'],
        "all": entries
    }
    return success_response(data=structured)

@planner_bp.route('', methods=['POST'])
@login_required
def create_entry():
    user_id = session['user_id']
    data = request.get_json() or {}
    
    entry_date = (data.get('date') or date.today().isoformat()).strip()
    if not validate_date(entry_date):
        return error_response("Date must be in YYYY-MM-DD format.", 400)

    section = (data.get('section') or '').strip().lower()
    if section not in VALID_SECTIONS:
        return error_response("Section must be one of: morning, afternoon, evening.", 400)

    content = (data.get('content') or '').strip()
    if not content:
        return error_response("Planner item content cannot be empty.", 400)

    entry = PlannerModel.create(
        user_id=user_id,
        date=entry_date,
        section=section,
        content=content
    )
    return success_response(data=entry, message="Planner entry created.", status_code=201)

@planner_bp.route('/<int:entry_id>', methods=['PUT'])
@login_required
def update_entry(entry_id):
    user_id = session['user_id']
    existing = PlannerModel.get_by_id(entry_id, user_id)
    if not existing:
        return error_response("Planner entry not found.", 404)

    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    if not content:
        return error_response("Content cannot be empty.", 400)

    updated = PlannerModel.update(entry_id, user_id, content)
    return success_response(data=updated, message="Planner entry updated.")

@planner_bp.route('/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    user_id = session['user_id']
    deleted = PlannerModel.delete(entry_id, user_id)
    if not deleted:
        return error_response("Planner entry not found.", 404)
    return success_response(message="Planner entry removed.")
