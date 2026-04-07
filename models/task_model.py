from models.db import get_db_connection

# --- TASKS ---
def get_tasks(user_id, role):
    conn = get_db_connection()

    if role == 'admin':
        # Admin sees everything
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY created_at DESC"
        ).fetchall()

        subtasks = conn.execute(
            "SELECT * FROM tasks WHERE parent_id IS NOT NULL"
        ).fetchall()

    else:
        # 1. Get Parent Tasks (Filtered by RBAC)
        tasks = conn.execute("""
        SELECT * FROM tasks
        WHERE parent_id IS NULL
        AND (user_id = ? OR assigned_role = ?)
        ORDER BY created_at DESC
        """, (user_id, role)).fetchall()

        # 2. Get Subtasks (Filtered by "Is my parent visible?")
        # We use a Subquery to find subtasks belonging to the tasks found above
        subtasks = conn.execute("""
        SELECT * FROM tasks
        WHERE parent_id IS NOT NULL
        AND parent_id IN (
            SELECT id FROM tasks 
            WHERE user_id = ? OR assigned_role = ?
        )
        """, (user_id, role)).fetchall()

    conn.close()
    return tasks, subtasks


def add_task_db(user_id, title, description, category, priority, due_date, username):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, title, description, category, priority, due_date, user_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, title, description, category, priority, due_date, username)
    )
    conn.commit()
    conn.close()


def add_subtask_db(user_id, parent_id, title, category, priority, username):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, parent_id, title, category, priority, user_name) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, parent_id, title, category, priority, username)
    )
    conn.commit()
    conn.close()


def delete_task_db(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def toggle_task_db(task_id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    new_status = 0 if task['is_completed'] else 1

    conn.execute(
        "UPDATE tasks SET is_completed = ? WHERE id = ?",
        (new_status, task_id)
    )

    # 🔥 if main task → update all subtasks
    if task['parent_id'] is None:
        conn.execute(
            "UPDATE tasks SET is_completed = ? WHERE parent_id = ?",
            (new_status, task_id)
        )

    conn.commit()
    conn.close()

    return new_status

def edit_task_db(task_id, field, value):
    allowed_fields = ['title', 'description', 'category', 'priority', 'due_date']
    if field not in allowed_fields:
        raise ValueError("Invalid field")
    
    conn = get_db_connection()
    conn.execute(f"UPDATE tasks SET {field} = ? WHERE id = ?", (value, task_id))
    conn.commit()
    conn.close()


def can_edit_task(task_id, role, user_id=None):
    conn = get_db_connection()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()
    conn.close()

    if not task:
        return False

    # Admin can edit anything
    if role == 'admin':
        return True

    # ONLY creator can edit
    return task['user_id'] == user_id
