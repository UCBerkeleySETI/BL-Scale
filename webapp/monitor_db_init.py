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

firebase_config = {
    "authDomain": "breakthrough-listen-sandbox.firebaseapp.com",
    "databaseURL": "https://breakthrough-listen-sandbox.firebaseio.com",
    "projectId": "breakthrough-listen-sandbox",
    "storageBucket": "breakthrough-listen-sandbox.appspot.com",
    "messagingSenderId": "848306815127",
    "appId": "1:848306815127:web:52de0d53e030cac44029d2",
    "measurementId": "G-STR7QLT26Q"
}
firebase_config["apiKey"] = os.environ["FIREBASE_API_KEY"]

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

def check_token_plus(self, database_url, path, access_token=None):
        if access_token:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, access_token)
        else:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, get_firebase_access_token())




pyrebase.pyrebase.Database.build_request_url = build_request_url_plus
pyrebase.pyrebase.Database.check_token = check_token_plus
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


db = firebase.database()
data = {
    "pod1":{
        "CPU":[1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,10,11],
        "RAM":[1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,10,11]
    }
}
db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").set(data)
print("done")