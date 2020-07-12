import os
import pyrebase
config = {
    "authDomain": "breakthrough-listen-sandbox.firebaseapp.com",
    "databaseURL": "https://breakthrough-listen-sandbox.firebaseio.com",
    "projectId": "breakthrough-listen-sandbox",
    "storageBucket": "breakthrough-listen-sandbox.appspot.com",
    "messagingSenderId": "848306815127",
    "appId": "1:848306815127:web:52de0d53e030cac44029d2",
    "measurementId": "G-STR7QLT26Q"
}
config["apiKey"]=os.environ["FIREBASE_API_KEY"]
# print(config["apiKey"])
email = "peterxiangyuanma@gmail.com"
password = "123456"
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)
user = auth.refresh(user['refreshToken'])
userIdToken = user['idToken']
os.environ["FIREBASE_SECRET_TOKEN"] = userIdToken
print(userIdToken)
print(os.environ["FIREBASE_SECRET_TOKEN"])