from flask import request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import Blueprint
from flask import current_app
from flask import render_template
import pandas as pd
import os

#makes blueprint named upload
upload = Blueprint('upload', __name__)


#initializes url
@upload.route('/input', methods = ['GET', 'POST'])
def input():
    if request.method == 'POST':
        if request.files: 
            CSVfile = request.files['file'] 
            filename = 'csv_file.csv'
            CSVfile.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
           
            return render_template('index.html')

@upload.route('/input_page')
def input_page():
    return render_template('input.html')
