import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from colorization import colorize

UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'png', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
     

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect('upload')

        file = request.files['file']

        if file.filename == '':
            return redirect('upload')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_full = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filename_full)
            processed_filename_full = colorize(filename_full)
            processed_filename = processed_filename_full.replace(app.config['UPLOAD_FOLDER'] + '\\', '')
            return redirect(url_for('result', before=filename, after=processed_filename))

    return render_template('upload.html')


@app.route('/result')
def result():
    uploads_url = 'http://127.0.0.1:5000/uploads/'
    img_before = uploads_url + request.args.get('before')
    img_after = uploads_url + request.args.get('after')
    return render_template('result.html', before=img_before, after=img_after)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run()