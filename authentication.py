import pyrebase

config={
      'apiKey': "AIzaSyA_xLGCT3PKw-FhqLnPaoCN1rbPqw1Yki0",
  'authDomain': "securityapps-17dd1.firebaseapp.com",
  'projectId': "securityapps-17dd1",
  'storageBucket': "securityapps-17dd1.appspot.com",
  'messagingSenderId': "623304704833",
  'appId': "1:623304704833:web:68aa81bea85c7742b817c0",
  'measurementId': "G-79RVK93615",
 'databaseURL': " "
}
user="testing@gmail.com"
password="1234567"
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user_signed=auth.create_user_with_email_and_password(user,password)
