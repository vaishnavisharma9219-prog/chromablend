from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import private_access_required
from backend.services.safety_service import generate_and_save_plan, VALID_SITUATIONS
from backend.services.ai_service import AIConfigurationError, AIServiceError
from backend.database.models import SafetyPlanModel

safety_bp = Blueprint('safety', __name__, url_prefix='/api/safety')

@safety_bp.route('/situations', methods=['GET'])
@private_access_required
def get_situations():
    """Return available scenario templates for safety planning."""
    return success_response(data=VALID_SITUATIONS)

@safety_bp.route('/plan', methods=['POST'])
@private_access_required
def generate_plan():
    user_id = session['user_id']
    data = request.get_json() or {}
    situation = (data.get('situation') or '').strip()
    input_details = (data.get('input_details') or '').strip()

    if not situation:
        return error_response("Please select a planning situation.", 400)

    try:
        plan_record = generate_and_save_plan(
            user_id=user_id,
            situation=situation,
            input_details=input_details
        )
        return success_response(
            data=plan_record,
            message="Safety plan generated and saved.",
            status_code=201
        )
    except AIConfigurationError as e:
        return error_response(str(e), 503)
    except AIServiceError as e:
        return error_response(str(e), 502)
    except Exception as e:
        return error_response(f"An error occurred while generating your plan: {str(e)}", 500)

@safety_bp.route('/plans', methods=['GET'])
@private_access_required
def get_plans():
    user_id = session['user_id']
    plans = SafetyPlanModel.get_all(user_id)
    return success_response(data=plans)

@safety_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@private_access_required
def delete_plan(plan_id):
    user_id = session['user_id']
    deleted = SafetyPlanModel.delete(plan_id, user_id)
    if not deleted:
        return error_response("Safety plan not found.", 404)
    return success_response(message="Safety plan removed.")
