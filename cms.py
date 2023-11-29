from flask import Flask, session, redirect, url_for, request, render_template, send_from_directory
import os

from markdown import markdown

app = Flask(__name__)

app.secret_key = 'secret'

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'test', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'data')

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
        session['message'] = f"{filename} does not exist."
        return redirect(url_for('index'))

@app.route("/<filename>/edit")
def edit_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return render_template('edit.html', filename=filename, content=content)
    else:
        session['message'] = f"{filename} does not exist."
        return redirect(url_for('index'))

@app.route("/<filename>", methods=['POST'])
def save_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    content = request.form['content']
    with open(file_path, 'w') as file:
        file.write(content)

    session['message'] = f"{filename} has been updated."
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5003)