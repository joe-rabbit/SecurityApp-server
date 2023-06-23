import os
import secrets
import shutil
import json
import socket
import time
import zipfile
from fastapi import FastAPI
from flask_socketio import SocketIO,emit
from fastapi import WebSocket
import subprocess
from functools import wraps
from functools import wraps
import logging
import pyrebase
import webbrowser
from flask import Flask, flash, request, redirect, send_file,render_template,jsonify,session,url_for
from werkzeug.utils import secure_filename
user_unique_id=None
# logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w')
UPLOAD_FOLDER = os.path.join('backup_data')
DOCS_EXTENSIONS = set(['txt', 'pdf','doc','docx','ppt','xlsx','apk'])
AUDIO_EXTENSIONS = set(['opus','mp3','mpeg', 'm4a', 'aac', 'mp4'])
IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','tif'])
user_name =  None
app = Flask(__name__)
config={
  'apiKey': "YOUR_API_KEY",
  'authDomain': "",
  'projectId': "",
  'storageBucket': "",
  'messagingSenderId': "",
  'appId': "",
  'measurementId': "",
 'databaseURL': " "
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secrets.token_hex(16)

socketio = SocketIO(app)

def allowed_file_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

def allowed_file_docs(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in DOCS_EXTENSIONS

def allowed_file_audio(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in AUDIO_EXTENSIONS

def login_required(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        user = firebase.auth().current_user
        if user is None:
            return redirect(url_for('login'))  # Redirect to login page if user is not authenticated
        else:
            return route_func(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods = ["POST","GET"])
def login():
    global user_unique_id
    if('user' in session):
        return render_template('download_main.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
    
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user']=email
  
        
            user_unique_id = user['localId']
            logging.info(str(user_unique_id))
            return render_template('download_main.html')
        except:
            return render_template('index.html', error='Invalid username or password')
    return render_template('index.html')


@app.route('/logout', methods = ["POST","GET"])
def logout():
    if request.method == "POST":
        session.pop('user')
    return render_template('index.html')
    
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # handle sign up form submission
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            return render_template('index.html')
        except:
            return render_template('signup.html', error='Email already exists')
      
    
    else:
        # render sign up form
        return render_template('signup.html')



@app.route('/call', methods=["POST", "GET"])

@socketio.on('message')
##make the app run in background for this to work 
def handle_message():
    message=request.form['phoneNumber']
    findphone_id=  str(user_unique_id) + "message"
    logging.info(findphone_id)
    socketio.emit(findphone_id, message)
    return render_template('download_main.html')


@app.route('/camera',methods=["GET", "POST"])

@socketio.on('camera')

def open_camera():
    findphone_id=  str(user_unique_id) + "camera"
    logging.info(findphone_id)
    socketio.emit(findphone_id,'camera')
    # socketio.emit('camera','camera')
    return render_template('download_main.html')

@app.route('/change',methods=["GET", "POST"])
def change_pasword():
    if request.method == "POST":
        email=request.form.get('email')
        try:
            user = auth.send_password_reset_email(email)
            return render_template('index.html')
        except:
            return render_template('change.html', error='Invalid Email ID')
    return render_template('changes.html')


@app.route('/findphone',methods=['GET', 'POST'])

def  find_phone():
    findphone_id=  str(user_unique_id) + "findphone"
    logging.info(findphone_id)
    socketio.emit(findphone_id,'findphone')
    return render_template('download_main.html')


@app.route('/gps', methods=['GET', 'POST'])
def handle_gps():
    if request.method == 'POST':
        # Retrieve the GPS coordinates from the request data
        data = request.data.decode('utf-8')
       
        # Emit the GPS data to all connected clients
        socketio.emit('gps_data', data)
        socketio.emit('gps', data)
        
    # Create a JSON file with the received data
    file_path = os.path.join(UPLOAD_FOLDER, 'location_data.json')
    time.sleep(20)
    with open(file_path,'r') as file :
        if file is not None:
                data = json.load(file)
                lat,lng = data[0],data[1]
                maps_url=f'https://www.google.com/maps?q={lat},{lng}'
                webbrowser.open(maps_url)


    return render_template('download_main.html')


@app.route('/received_gps', methods=['POST'])
def received_gps():
    data = request.get_json()
    coods = data.get('coords',[])

    # Create a JSON file with the received data
    file_path = os.path.join(UPLOAD_FOLDER, 'location_data.json')
    with open(file_path, 'w') as file:
        json.dump(coods, file)
    if file_path is FileNotFoundError:
        with open(file_path,'r') as file :
            if file is not None:
                data = json.load(file)
                lat,lng = data[0],data[1]
                maps_url=f'https://www.google.com/maps?q={lat},{lng}'
                webbrowser.open_new(maps_url)



    response = {'message': 'GPS data received'}
    return jsonify(response)

@app.route('/foundphone',methods=['GET','POST'])

def foundphone():
    findphone_id=  str(user_unique_id) + "foundphone"
    logging.info(findphone_id)
    socketio.emit(findphone_id,'foundphone')
 
    return render_template('download_main.html')


   

@app.route('/upload_images_illegal_access', methods=["POST","GET"])
def upload_files():
    if request.method == 'POST':
        # Check if files were uploaded
        if 'uploaded-file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        # Get uploaded files
        files = request.files.getlist('uploaded-file')
        
        # Check if any files have a name
        for file in files:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
        
        # Check if all files are allowed
        for file in files:
            if not allowed_file_image(file.filename):
                print('Invalid file type')
                return redirect(request.url)
        

            uploaded_images_dir = os.path.join(app.config['UPLOAD_FOLDER'], "upload_images_illegal_access")
        if not os.path.exists(uploaded_images_dir):
            os.makedirs(uploaded_images_dir)
        
        for file in files:
            filename = secure_filename(file.filename)
            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            moved_file_path = os.path.join(uploaded_images_dir, filename)
            file.save(uploaded_file_path)
            shutil.move(uploaded_file_path, moved_file_path)
        
        print('Files uploaded successfully')
        return redirect(request.url)
        
    return '''  sucesss '''


@app.route('/upload_images', methods=["POST","GET"])
def upload_file():
    if request.method == 'POST':
        # Check if files were uploaded
        if 'uploaded-file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        # Get uploaded files
        files = request.files.getlist('uploaded-file')
        
        # Check if any files have a name
        for file in files:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
        
        # Check if all files are allowed
        for file in files:
            if not allowed_file_image(file.filename):
                print('Invalid file type')
                return redirect(request.url)
        

            uploaded_images_dir = os.path.join(app.config['UPLOAD_FOLDER'], "uploaded_images")
        if not os.path.exists(uploaded_images_dir):
            os.makedirs(uploaded_images_dir)
        
        for file in files:
            filename = secure_filename(file.filename)
            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            moved_file_path = os.path.join(uploaded_images_dir, filename)
            file.save(uploaded_file_path)
            shutil.move(uploaded_file_path, moved_file_path)
        
        print('Files uploaded successfully')
        return redirect(request.url)
        
    return '''  sucesss '''


@app.route('/upload_docs', methods=["POST","GET"])
def upload_docs():
    if request.method == 'POST':
        # Check if file was uploaded
         if 'uploaded-file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        # Get uploaded file
    file = request.files['uploaded-file']
        
        # Check if file has a name
    if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        #For documents 
    if file and allowed_file_docs(file.filename):
            filename = secure_filename(file.filename)
      
            uploaded_file_dir = os.path.join(app.config['UPLOAD_FOLDER'],  "uploaded_documents"+str(user_name))
            if not os.path.exists(uploaded_file_dir):
                os.makedirs(uploaded_file_dir)

            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            moved_file_path = os.path.join(uploaded_file_dir, filename)
            file.save(uploaded_file_path)
            shutil.move(uploaded_file_path, moved_file_path)
            print("File Uploaded Successfully")
    else:
            print('Invalid file type')
            return(redirect)
    return '''  sucesss '''

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'uploaded-file' not in request.files:
        app.logger.error('No file part')
        return print('No file part', 400)

    file = request.files['uploaded-file']

    if file.filename == '':
        app.logger.error('No selected file')
        return print('No selected file', 400)

    if not allowed_file_audio(file.filename):
        app.logger.error('Invalid file type')
        return print('Invalid file type', 400)

    filename = secure_filename(file.filename)

    uploaded_file_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_audio_files')
    os.makedirs(uploaded_file_dir, exist_ok=True)

    uploaded_file_path = os.path.join(uploaded_file_dir, filename)
    file.save(uploaded_file_path)

    app.logger.info('File uploaded successfully')
   
    return '''  sucesss '''
     

# 
 #For apk files
   
                


     

@app.route('/downloads', methods=["POST","GET"])
def download_file():
    if request.method == 'POST':
        folder_path = UPLOAD_FOLDER
        
        if os.path.isdir(folder_path):
            temp_file = shutil.make_archive("backed_up_data", "zip", folder_path)
            shutil.move(temp_file, folder_path)
            response = send_file(os.path.join(UPLOAD_FOLDER,os.path.basename(temp_file)), as_attachment=True)
         
            return response
        else:
            return jsonify({"error": "uploaded_images directory does not exist"})
    else:
        return jsonify({"error":"unsuccessful"})

  

@app.route('/delete_images', methods=["GET"])
def delete_files():
    if request.method == 'GET':
        folder_path = UPLOAD_FOLDER
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Delete all .zip files in directory
        for file in os.listdir(UPLOAD_FOLDER):
            if file.endswith(".zip"):
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, file))
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file, e))

        return jsonify({"message": "successfully deleted"})
    else:
        return jsonify({"error": "unsuccessful"})



   


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0',port=5000)
