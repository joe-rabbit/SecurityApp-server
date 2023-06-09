import pyrebase

config={

}
user="testing@gmail.com"
password="1234567"
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user_signed=auth.create_user_with_email_and_password(user,password)
