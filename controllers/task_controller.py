from flask import request, session, jsonify
from models.task_model import get_tasks, delete_task_db
from services.task_service import update_progress
from models.db import get_db_connection


def dashboard_controller():
    tasks, subtasks = get_tasks(session['user_id'], session['role'])
    return tasks, subtasks


def delete_task_controller(task_id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if not task:
        return {'error': 'Not found'}, 404

    if session['role'] != 'admin' and task['user_id'] != session['user_id']:
        return {'error': 'Forbidden'}, 403

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return '', 204


