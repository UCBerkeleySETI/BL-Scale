import os
import time
import pyrebase
from urllib.parse import urlencode
from google.oauth2 import service_account


def pyrebase_cred_wrapper():
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
        """Creates a generator that generates up-to-date access tokens for firebase

        Returns
        -------
        Generator
            Generator that yields firebase access tokens

        """
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
        """Wrapper for access token generator

        Returns
        -------
        string
            Firebase access token from the token generator

        """
        return next(token_gen)

    def build_request_url_plus(self, access_token=None):
        """Replacement for the broken `build_request_url` in pyrebase
           Undos extra quotes that render the request urls invalid

        Parameters
        ----------
        access_token : string
            takes in supplied access token if there is one,
            if not, token from token generator is used

        Returns
        -------
        string
            request url for the generated request, with correct access token

        """
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
        """Replacement for broken `check_token` in pyrebase

        Parameters
        ----------
        database_url : string
            url of the firebase database
        path : string
            path to the requested object in the databse
        access_token : string
            takes in supplied access token if there is one,
            if not, token from token generator is used

        Returns
        -------
        type
            Correct url with access token

        """
        if access_token:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, access_token)
        else:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, get_firebase_access_token())

    pyrebase.pyrebase.Database.build_request_url = build_request_url_plus
    pyrebase.pyrebase.Database.check_token = check_token_plus
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    return firebase, db
