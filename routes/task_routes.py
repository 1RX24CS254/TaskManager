from flask import render_template, Blueprint, request, session, jsonify
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
    toggle_task_db,
    can_edit_task
)
from services.task_service import update_progress
from models.db import get_db_connection

task_routes = Blueprint('task_routes', __name__)

# ---------------- DASHBOARD ----------------
@task_routes.route('/dashboard', methods=['GET'])
def dashboard():
    tasks, subtasks = dashboard_controller()
    # convert sqlite Row objects to dict
#    return jsonify({
#        "tasks": [dict(t) for t in tasks],
#        "subtasks": [dict(s) for s in subtasks]
#    })
    return render_template('index.html', tasks=tasks, subtasks=subtasks)

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

    if not data.get('title') or not data.get('title').strip():
        return jsonify({'error': 'Title required'}), 400

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
    if not can_edit_task(task_id, session['role'], session['user_id']):
        return {'error': 'Forbidden'}, 403

    return delete_task_controller(task_id)

# ---------------- EDIT TASK ----------------
@task_routes.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    # DAC check
    if not can_edit_task(task_id, session['role'], session['user_id']):
        return {'error': 'Forbidden'}, 403

    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    edit_task_db(task_id, field, value)
    return jsonify({'success': True})

# ---------------- TOGGLE TASK ----------------
@task_routes.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    if not can_edit_task(task_id, session['role']):
        return {'error': 'Forbidden'}, 403
    new_status = toggle_task_db(task_id)
    # if main task, update subtasks and progress
    update_progress(task_id)
    return '', 204

@task_routes.route('/delete_subtask/<int:sub_id>', methods=['DELETE'])
def delete_subtask(sub_id):
    conn = get_db_connection()

    sub = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (sub_id,)
    ).fetchone()

    if not sub:
        conn.close()
        return {'error': 'Not found'}, 404

    parent_id = sub['parent_id']

    conn.execute("DELETE FROM tasks WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()

    # ✅ safe call
    if parent_id:
        update_progress(parent_id)

    return '', 204

    return '', 204

@task_routes.route('/edit_subtask/<int:sub_id>', methods=['POST'])
def edit_subtask(sub_id):
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')

    allowed = ['title', 'category', 'priority']
    if field not in allowed:
        return {'error': 'Invalid field'}, 400

    conn = get_db_connection()
    conn.execute(
        f"UPDATE tasks SET {field} = ? WHERE id = ?",
        (value, sub_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@task_routes.route('/assign_role', methods=['POST'])
def assign_role():
    if session['role'] != 'admin':
        return {'error': 'Forbidden'}, 403

    data = request.get_json()
    task_id = data.get('task_id')
    role = data.get('role')

    conn = get_db_connection()
    conn.execute(
        "UPDATE tasks SET assigned_role = ? WHERE id = ?",
        (role, task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})

    