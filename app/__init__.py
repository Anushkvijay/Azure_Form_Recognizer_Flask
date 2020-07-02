# imports
from flask import Flask,session,url_for,render_template,request,redirect,send_file
from config import Config
import os,json
from werkzeug.utils import secure_filename
from app.formrecognizer import FormRecognize
import pandas as pd

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config) #initializing config object to use in app module

ALLOWED_EXTENSIONS = set(['pdf', 'jpg', 'jpeg', 'tiff']) #allowed extensions for uploading file

if (__name__) == "__main__":
    app.run(debug=True)

#function to check if correct file type is uploaded
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#route render home/index page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

#analyze uploaded file and provide user with choice to save results
@app.route('/submit', methods = ['GET', 'POST'])
# @cache.cached(timeout=50)
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #uploading file
            
        filetype = filename.split(".")[-1] #getting filetype
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result_url = FormRecognize.analyze(filepath,filetype)
        FormRecognize.analyze_results(result_url)
        df = FormRecognize.parseresults()
        session['data'] = df.to_json()

    return render_template("selectfile.html")

#download csv
@app.route('/csv', methods = ['POST', 'GET'])
def downloadcsv():
    data_type = 'csv'
    dat = session.get('data',None)
    data = pd.read_json(dat, dtype=False)
    FormRecognize.save_data(data_type,data)
    return send_file('E:/Quarantine/Form Recognizer/form_data.csv', as_attachment=True, attachment_filename='data.csv')

#store to sql server
@app.route('/sql', methods = ['POST', 'GET'])
def downloadsql():
    data_type = 'sql'
    dat = session.get('data',None)
    data = pd.read_json(dat, dtype=False)
    FormRecognize.save_data(data_type,data)
    return redirect(url_for('upload_file'))

#download xlsx
@app.route('/xlsx', methods = ['POST', 'GET'])
def downloadxlsx():
    data_type = 'xlsx'
    dat = session.get('data',None)
    data = pd.read_json(dat, dtype=False)
    FormRecognize.save_data(data_type,data)
    return send_file('E:/Quarantine/Form Recognizer/form_data.xlsx', as_attachment=True, attachment_filename='data.xlsx')

#download txt file
@app.route('/txt', methods = ['POST', 'GET'])
def downloadtxt():
    data_type = 'txt'
    dat = session.get('data',None)
    data = pd.read_json(dat, dtype=False)
    FormRecognize.save_data(data_type,data)
    return send_file('E:/Quarantine/Form Recognizer/form_data.txt', as_attachment=True, attachment_filename='data.txt')