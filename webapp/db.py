from firebase import firebase
import pyrebase 

# First bit is pyrebase

config = {
    "apiKey": "AIzaSyAWVDszEVzJ_GSopx-23slhwKM2Ha5qkbw",
    "authDomain": "breakthrough-listen-sandbox.firebaseapp.com",
    "databaseURL": "https://breakthrough-listen-sandbox.firebaseio.com",
    "projectId": "breakthrough-listen-sandbox",
    "storageBucket": "breakthrough-listen-sandbox.appspot.com",
    "messagingSenderId": "848306815127",
    "appId": "1:848306815127:web:52de0d53e030cac44029d2",
    "measurementId": "G-STR7QLT26Q"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
users = db.child("breakthrough-listen-sandbox").child("flask_vars").get()
print(users.val())


#updating a specific record 
db.child("breakthrough-listen-sandbox").child("flask_vars").child("-MBkt_yIVsUfiHB4WF7c").update({"Message": "Mortiest Morty"})
# Writing data
data = {"Message": "karen"}
db.child("breakthrough-listen-sandbox").child("flask_vars").push(data)

# # Posting data
# firebase = firebase.FirebaseApplication('https://breakthrough-listen-sandbox.firebaseio.com/', None)
# data =  { 'Message': 'test_send_one'}
# result = firebase.post('/breakthrough-listen-sandbox/flask_vars',data)


# # Reading in data
# retrieved = firebase.get('/breakthrough-listen-sandbox/flask_vars', '')
# print(retrieved)

# # Updating Data

# retrieved = firebase.put('/breakthrough-listen-sandbox/flask_vars/-MBkt_yIVsUfiHB4WF7c', 'Message', 'Bob')
# print('Updated database')


# # Delete data 
# retrieved = firebase.delete('/breakthrough-listen-sandbox/flask_vars/', '-MBkt_yIVsUfiHB4WF7c')
# print('Deleted Record')

# # Full video here https://www.youtube.com/watch?v=rKuGCQda_Qo 