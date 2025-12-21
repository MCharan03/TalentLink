from flask import render_template, send_from_directory, current_app
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
