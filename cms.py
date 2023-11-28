from flask import Flask, session, redirect, url_for, render_template, send_from_directory
import os

app = Flask(__name__)

app.secret_key = 'secret'

@app.route("/")
def index():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "data")
    files = [os.path.basename(path) for path in os.listdir(data_dir)]
    return render_template('index.html', files=files)

@app.route("/<filename>")
def file_content(filename):
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "data")
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        return send_from_directory(data_dir, filename, as_attachment=False)
    else:
        session['message'] = f"{filename} does not exist."
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5003)