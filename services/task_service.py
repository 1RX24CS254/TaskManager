from models.db import get_db_connection

def update_progress(task_id):
    conn = get_db_connection()

    subs = conn.execute(
        "SELECT is_completed FROM tasks WHERE parent_id = ?",
        (task_id,)
    ).fetchall()

    if not subs:
        conn.close()
        return

    total = len(subs)
    completed = sum(1 for s in subs if s['is_completed'])

    percent = int((completed / total) * 100)

    # update progress
    conn.execute(
        "UPDATE tasks SET progress_percent = ? WHERE id = ?",
        (percent, task_id)
    )

    # 🔥 also update parent completion status
    if completed == total:
        conn.execute("UPDATE tasks SET is_completed = 1 WHERE id = ?", (task_id,))
    elif completed == 0:
        conn.execute("UPDATE tasks SET is_completed = 0 WHERE id = ?", (task_id,))
    else:
        conn.execute("UPDATE tasks SET is_completed = 0 WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()