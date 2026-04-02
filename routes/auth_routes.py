from flask import Blueprint, request, session, redirect, url_for, flash, jsonify
from models.db import get_db_connection
from werkzeug.security import check_password_hash

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('task_routes.dashboard'))
    return jsonify({'message': 'Login required'})  # Or render_template('login.html')

@auth_routes.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('task_routes.dashboard'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('auth_routes.index'))

@auth_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_routes.index'))


