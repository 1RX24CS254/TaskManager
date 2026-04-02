from flask import Blueprint, request, session, jsonify
from controllers.task_controller import (
    dashboard_controller,
    delete_task_controller
)
from models.task_model import (
    get_tasks,
    delete_task_db,
    add_task_db,
    add_subtask_db,
    edit_task_db,
    toggle_task_db
)
from services.task_service import update_progress

task_routes = Blueprint('task_routes', __name__)

# ---------------- DASHBOARD ----------------
@task_routes.route('/dashboard', methods=['GET'])
def dashboard():
    tasks, subtasks = dashboard_controller()
    # convert sqlite Row objects to dict
    return jsonify({
        "tasks": [dict(t) for t in tasks],
        "subtasks": [dict(s) for s in subtasks]
    })

# ---------------- ADD TASK ----------------
@task_routes.route('/add', methods=['POST'])
def add_task():
    data = request.get_json()
    add_task_db(
        user_id=session['user_id'],
        username=session['username'],
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        priority=data.get('priority'),
        due_date=data.get('due_date')
    )
    return jsonify({'success': True})

# ---------------- ADD SUBTASK ----------------
@task_routes.route('/add_subtask/<int:parent_id>', methods=['POST'])
def add_subtask(parent_id):
    data = request.get_json()
    add_subtask_db(
        user_id=session['user_id'],
        username=session['username'],
        parent_id=parent_id,
        title=data.get('title'),
        category=data.get('category'),
        priority=data.get('priority')
    )
    update_progress(parent_id)
    return jsonify({'success': True})

# ---------------- DELETE TASK ----------------
@task_routes.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return delete_task_controller(task_id)

# ---------------- EDIT TASK ----------------
@task_routes.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    edit_task_db(task_id, field, value)
    return jsonify({'success': True})

# ---------------- TOGGLE TASK ----------------
@task_routes.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    new_status = toggle_task_db(task_id)
    # if main task, update subtasks and progress
    update_progress(task_id)
    return '', 204


