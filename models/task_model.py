from models.db import get_db_connection

# --- TASKS ---
def get_tasks(user_id, role):
    conn = get_db_connection()

    # Admin can see all
    if role == 'admin':
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY created_at DESC"
        ).fetchall()
        subtasks = conn.execute(
            "SELECT * FROM tasks WHERE parent_id IS NOT NULL"
        ).fetchall()
    else:
        # Apply DAC: check task_access table
        tasks = conn.execute("""
            SELECT t.*
            FROM tasks t
            LEFT JOIN task_access a
                ON t.id = a.task_id AND a.role = ?
            WHERE t.parent_id IS NULL
              AND (a.can_view=1 OR a.id IS NULL)
            ORDER BY t.created_at DESC
        """, (role,)).fetchall()

        subtasks = conn.execute("""
            SELECT t.*
            FROM tasks t
            LEFT JOIN task_access a
                ON t.id = a.task_id AND a.role = ?
            WHERE t.parent_id IS NOT NULL
              AND (a.can_view=1 OR a.id IS NULL)
        """, (role,)).fetchall()

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
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    if not task:
        return False  # Task doesn't exist

    # Admin can edit anything
    if role == 'admin':
        return True

    # Owner of the task can edit
    if user_id and task['user_id'] == user_id:
        return True

    # Professors or other roles: implement your rules
    # Example: allow 'professor' to edit tasks in 'School' category
    if role == 'professor' and task['category'] == 'School':
        return True

    return False  # Default deny

def can_delete_task(task_id, role):
    conn = get_db_connection()
    access = conn.execute(
        "SELECT can_delete FROM task_access WHERE task_id=? AND role=?",
        (task_id, role)
    ).fetchone()
    conn.close()
    return access['can_delete'] == 1 if access else False
