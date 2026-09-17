from flask import Blueprint, request, session
from backend.utils.responses import success_response, error_response
from backend.utils.security import login_required
from backend.database.models import TaskModel

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    date = request.args.get('date')
    completed_param = request.args.get('completed')
    completed = int(completed_param) if completed_param in ('0', '1') else None

    tasks = TaskModel.get_all(user_id, date=date, completed=completed)
    return success_response(data=tasks)

@tasks_bp.route('', methods=['POST'])
@login_required
def create_task():
    user_id = session['user_id']
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()

    if not title:
        return error_response("Task title is required.", 400)

    description = (data.get('description') or '').strip()
    date = data.get('date') or None
    time = data.get('time') or None
    priority = data.get('priority') or 'normal'

    task = TaskModel.create(
        user_id=user_id,
        title=title,
        description=description,
        date=date,
        time=time,
        priority=priority
    )
    return success_response(data=task, message="Task created.", status_code=201)

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    user_id = session['user_id']
    task = TaskModel.get_by_id(task_id, user_id)
    if not task:
        return error_response("Task not found.", 404)
    return success_response(data=task)

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    user_id = session['user_id']
    existing = TaskModel.get_by_id(task_id, user_id)
    if not existing:
        return error_response("Task not found.", 404)

    data = request.get_json() or {}
    title = (data.get('title') or existing['title']).strip()
    if not title:
        return error_response("Task title cannot be empty.", 400)

    description = data.get('description', existing['description'])
    date = data.get('date', existing['date'])
    time = data.get('time', existing['time'])
    completed = data.get('completed', existing['completed'])
    priority = data.get('priority', existing['priority'])

    updated = TaskModel.update(
        task_id=task_id,
        user_id=user_id,
        title=title,
        description=description,
        date=date,
        time=time,
        completed=completed,
        priority=priority
    )
    return success_response(data=updated, message="Task updated.")

@tasks_bp.route('/<int:task_id>/toggle', methods=['PATCH'])
@login_required
def toggle_task(task_id):
    user_id = session['user_id']
    task = TaskModel.toggle_complete(task_id, user_id)
    if not task:
        return error_response("Task not found.", 404)
    return success_response(data=task, message="Task status updated.")

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    user_id = session['user_id']
    deleted = TaskModel.delete(task_id, user_id)
    if not deleted:
        return error_response("Task not found.", 404)
    return success_response(message="Task deleted successfully.")
