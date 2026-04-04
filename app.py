import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash

app = Flask(__name__)
# IMPORTANT: Change this to a random string for production
app.secret_key = 'fedora_task_manager_secret'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def index():
    # If already logged in, skip the login page and go to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    # Check if user exists and password hash matches
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    # Only fetch tasks belonging to the logged-in user
    if session['role'] == 'admin':
        tasks = conn.execute(
        "SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY created_at DESC"
        ).fetchall()

        subtasks = conn.execute(
        "SELECT * FROM tasks WHERE parent_id IS NOT NULL"
        ).fetchall()
    else:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND parent_id IS NULL ORDER BY created_at DESC",
            (session['user_id'],)
            ).fetchall()

        subtasks = conn.execute(
            "SELECT * FROM tasks WHERE parent_id IS NOT NULL AND user_id = ?",
            (session['user_id'],)
            ).fetchall()
    
    conn.close()
    
    return render_template('index.html', tasks=tasks, subtasks=subtasks)

@app.route('/add', methods=['POST'])
def add_task():

    data = request.get_json()

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO tasks 
        (user_id, title, description, category, priority, due_date, user_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session['user_id'],
        data.get('title'),
        data.get('description'),
        data.get('category'),
        data.get('priority'),
        data.get('due_date'),
        session['username']
    ))

    conn.commit()
    conn.close()

    return {'success': True}

@app.route('/add_subtask/<int:parent_id>', methods=['POST'])
def add_subtask(parent_id):
    data = request.get_json()

    conn = get_db_connection()
    conn.execute("""
    INSERT INTO tasks (user_id, parent_id, title, category, priority, user_name)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
    session['user_id'],
    parent_id,
    data.get('title'),
    data.get('category'),
    data.get('priority'),
    session['username']
))

    conn.commit()
    conn.close()

    return {'success': True}

def update_progress(task_id):
    conn = get_db_connection()

    subtasks = conn.execute(
        "SELECT is_completed FROM tasks WHERE parent_id = ?",
        (task_id,)
    ).fetchall()

    if not subtasks:
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

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (id,)
    ).fetchone()

    if not task:
        return {'error': 'Not found'}, 404

    # Allow admin OR owner
    if session['role'] != 'admin' and task['user_id'] != session['user_id']:
        return {'error': 'Forbidden'}, 403

    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return '', 204

@app.route('/edit/<int:id>', methods=['POST'])
def edit_task(id):
    data = request.get_json()

    field = data.get('field')
    value = data.get('value')

    allowed_fields = ['title', 'description', 'category', 'priority', 'due_date']

    if field not in allowed_fields:
        return {'error': 'Invalid field'}, 400

    conn = get_db_connection()
    conn.execute(f"UPDATE tasks SET {field} = ? WHERE id = ?", (value, id))
    conn.commit()
    conn.close()

    return {'success': True}

@app.route('/toggle/<int:id>', methods=['POST'])
def toggle_task(id):
    conn = get_db_connection()

    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()

    new_status = 0 if task['is_completed'] else 1

    conn.execute(
        "UPDATE tasks SET is_completed = ? WHERE id = ?",
        (new_status, id)
    )

    # update parent progress
    if task['parent_id']:
        update_progress(task['parent_id'])
    else:
    # if main task toggled, mark all subtasks same status
        conn.execute(
            "UPDATE tasks SET is_completed = ? WHERE parent_id = ?",
            (new_status, id)
            )
        update_progress(id)

    conn.commit()
    conn.close()

    return '', 204

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=24254)
