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
            "SELECT * FROM tasks ORDER BY created_at DESC"
        ).fetchall()
    else:
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', 
                         (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('index.html', tasks=tasks)

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
        INSERT INTO tasks (user_id, parent_id, title, user_name)
        VALUES (?, ?, ?, ?)
    """, (session['user_id'], parent_id, data.get('title'), session['username']))

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
    if session['role'] != 'admin':
        return {'error': 'Forbidden'}, 403

    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return '', 204

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

    conn.commit()
    conn.close()

    return '', 204

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=24254)
