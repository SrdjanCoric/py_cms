from flask import Flask, session, redirect, url_for, request, render_template, send_from_directory, flash
from functools import wraps
import os
import yaml
import bcrypt

from markdown import markdown

app = Flask(__name__)

app.secret_key = 'secret'

app.config['TESTING'] = True

def get_data_path():
    return os.path.join(os.path.dirname(__file__), 'data')

def user_signed_in():
    return 'username' in session

from functools import wraps

def require_signed_in_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not user_signed_in():
            flash("You must be signed in to do that.")
            return redirect(url_for('show_signin_form'))
        return f(*args, **kwargs)
    return decorated_function

def load_user_credentials():
    filename = 'test_users.yml' if app.config['TESTING'] else 'users.yml'
    credentials_path = os.path.join(os.path.dirname(__file__), filename)
    with open(credentials_path, 'r') as file:
        return yaml.safe_load(file)

def valid_credentials(username, password):
    credentials = load_user_credentials()

    if username in credentials:
        stored_password = credentials[username].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    else:
        return False

@app.route("/")
def index():
    data_dir = get_data_path()
    files = [os.path.basename(path) for path in os.listdir(data_dir)]
    return render_template('index.html', files=files)

@app.route("/<filename>")
def file_content(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
            if filename.endswith('.md'):
                with open(file_path, 'r') as file:
                    content = file.read()
                return markdown(content)
            else:
                return send_from_directory(data_dir, filename, as_attachment=False)
    else:
        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))

@app.route("/<filename>/edit")
@require_signed_in_user
def edit_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return render_template('edit.html', filename=filename, content=content)
    else:
        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))

@app.route("/<filename>", methods=['POST'])
@require_signed_in_user
def save_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    content = request.form['content']
    with open(file_path, 'w') as file:
        file.write(content)

    flash(f"{filename} has been updated.")
    return redirect(url_for('index'))

@app.route("/new")
@require_signed_in_user
def new_document():
    return render_template('new.html')

@app.route("/create", methods=['POST'])
@require_signed_in_user
def create_file():
    filename = request.form.get('filename', '').strip()
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if len(filename) == 0:
        flash("A name is required.")
        return render_template('new.html'), 422
    elif os.path.exists(file_path):
        flash(f"{filename} already exists.")
        return render_template('new.html'), 422
    else:
        with open(file_path, 'w') as file:
            file.write("")
        flash(f"{filename} has been created.")
        return redirect(url_for('index'))

@app.route("/<filename>/delete", methods=['POST'])
@require_signed_in_user
def delete_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{filename} has been deleted.")
    else:
        flash(f"{filename} does not exist.")

    return redirect(url_for('index'))

@app.route("/users/signin", methods=['GET'])
def show_signin_form():
    return render_template('signin.html')

@app.route("/users/signin", methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if valid_credentials(username, password):
        session['username'] = username
        flash("Welcome!")
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials")
        return render_template('signin.html'), 422

@app.route("/users/signout", methods=['POST'])
def signout():
    session.pop('username', None)
    flash("You have been signed out.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)