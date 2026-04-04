from flask import Flask, render_template, session, redirect, url_for
from routes.task_routes import task_routes
from routes.auth_routes import auth_routes

app = Flask(__name__)
app.secret_key = 'fedora_task_manager_secret'

app.register_blueprint(task_routes)
app.register_blueprint(auth_routes)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('task_routes.dashboard'))
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=24254)


