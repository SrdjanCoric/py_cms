from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

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
    return send_from_directory(data_dir, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, port=5003)