import os
import time
import pyrebase
import json
import requests
from requests import Session
from requests.exceptions import HTTPError
import urllib.request, json
from urllib.parse import urlencode, quote
from google.oauth2 import service_account

config = {
    "authDomain": "breakthrough-listen-sandbox.firebaseapp.com",
    "databaseURL": "https://breakthrough-listen-sandbox.firebaseio.com",
    "projectId": "breakthrough-listen-sandbox",
    "storageBucket": "breakthrough-listen-sandbox.appspot.com",
    "messagingSenderId": "848306815127",
    "appId": "1:848306815127:web:52de0d53e030cac44029d2",
    "measurementId": "G-STR7QLT26Q"
}
config["apiKey"] = os.environ["FIREBASE_API_KEY"]

def access_token_generator():
    from google.auth.transport.requests import Request

    scopes = ["https://www.googleapis.com/auth/firebase.database",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/cloud-platform"]
    credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=scopes)

    last_refreshed_at = time.time()
    request = Request()
    credentials.refresh(request)
    access_token = credentials.token

    while True:
        if (time.time() - last_refreshed_at) > 1800:
            last_refreshed_at = time.time()
            request = Request()
            credentials.refresh(request)
            access_token = credentials.token
        yield access_token

token_gen = access_token_generator()

def get_firebase_access_token():
    return next(token_gen)

def build_request_url_plus(self, access_token=None):
    parameters = {}
    if access_token:
        parameters['access_token'] = access_token
    else:
        parameters['access_token'] = get_firebase_access_token()
    for param in list(self.build_query):
        if type(self.build_query[param]) is str:
            parameters[param] = f"\"{self.build_query[param]}\""
        elif type(self.build_query[param]) is bool:
            parameters[param] = "true" if self.build_query[param] else "false"
        else:
            parameters[param] = self.build_query[param]
    # reset path and build_query for next query
    request_ref = f"{self.database_url}{self.path}.json?{urlencode(parameters)}"
    self.path = ""
    self.build_query = {}
    return request_ref

pyrebase.pyrebase.Database.build_request_url = build_request_url_plus
firebase = pyrebase.initialize_app(config)
db = firebase.database()





# print(users.val())


#updating a specific record
# db.child("breakthrough-listen-sandbox").child("flask_vars").child("-MBkt_yIVsUfiHB4WF7c").update({"Message": "Mortiest Morty"})
# Writing data


# data = {"done": True, "message": "Energy Detection Done....", "object_uri":"1","processing_time":8000, "timestamp":190}

# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP67287").set(data)
# data = {"done": True, "message": "Energy Detection Done....", "object_uri":"2","processing_time":8000, "timestamp":90}
# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP1907").set(data)
# data = {"done": True, "message": "Energy Detection Done....", "object_uri":"3","processing_time":8000, "timestamp":290}
# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP6111").set(data)
# data = {"done": True, "message": "Energy Detection Done....", "object_uri":"4","processing_time":8000, "timestamp":81}
# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP62227").set(data)
# data = {"done": True, "message": "Energy Detection Done updated....", "object_uri":"5","processing_time":8000, "timestamp":4000}
# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP67287").set(data)
# data = {"done": True, "message": "Energy Detection Done", "object_uri":"5","processing_time":8000, "timestamp":4000}
# db.child("breakthrough-listen-sandbox").child("flask_vars").child('test_sub').child("HIP2910").set(data)
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
