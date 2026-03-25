import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash
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
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', 
                         (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('index.html', tasks=tasks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=28254)
