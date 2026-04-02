from models.db import get_db_connection

def update_progress(task_id):
    conn = get_db_connection()

    subtasks = conn.execute(
        "SELECT is_completed FROM tasks WHERE parent_id = ?",
        (task_id,)
    ).fetchall()

    if not subtasks:
        conn.close()
        return

    total = len(subtasks)
    done = sum(s['is_completed'] for s in subtasks)

    percent = int((done / total) * 100)

    conn.execute(
        "UPDATE tasks SET progress_percent = ? WHERE id = ?",
        (percent, task_id)
    )

    conn.commit()
    conn.close()


