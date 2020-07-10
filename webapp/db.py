from firebase import firebase
import pyrebase 
import json
import requests
from requests import Session
from requests.exceptions import HTTPError
import urllib.request, json 
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


def query_by_order(db, order_by, limit_to, token):
    users = db.child("breakthrough-listen-sandbox").child("flask_vars").child("obs").order_by_child(order_by).limit_to_last(limit_to)
    request_edit = db.build_request_url(token)
    request_edit = request_edit.replace("%2522", "%22")


    with urllib.request.urlopen(request_edit) as url:
        data = json.loads(url.read().decode())
        return data

# data = query_by_order(db,order_by = "time",limit_to=3,token=False )
# print(data)





# print(users.val())


#updating a specific record 
# db.child("breakthrough-listen-sandbox").child("flask_vars").child("-MBkt_yIVsUfiHB4WF7c").update({"Message": "Mortiest Morty"})
# Writing data


data = {"done": True, "message": "Energy Detection Done....", "object_uri":"1","processing_time":8000, "timestamp":190}

db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP67287").set(data)
data = {"done": True, "message": "Energy Detection Done....", "object_uri":"2","processing_time":8000, "timestamp":90}
db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP1907").set(data)
data = {"done": True, "message": "Energy Detection Done....", "object_uri":"3","processing_time":8000, "timestamp":290}
db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP6111").set(data)
data = {"done": True, "message": "Energy Detection Done....", "object_uri":"4","processing_time":8000, "timestamp":81}
db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP62227").set(data)
data = {"done": True, "message": "Energy Detection Done updated....", "object_uri":"5","processing_time":8000, "timestamp":4000}
db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP67287").set(data)
data = {"done": True, "message": "Energy Detection Done", "object_uri":"5","processing_time":8000, "timestamp":4000}
db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP2910").set(data)
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