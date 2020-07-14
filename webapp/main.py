import pyrebase
from flask import render_template, request, redirect, session
import os
import base64
import io
import asyncio
import re
import pyrebase
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zmq
import time
import pickle
import logging
from google.cloud import storage
from flask import render_template, request, redirect, session, Flask
import time
import os
import threading
global cache
import time
import multiprocessing
import urllib.request, json
from urllib.parse import urlencode, quote
from google.oauth2 import service_account
import utils
from PIL import Image
import os.path
from os import path
import random 
import string 
cache = {}

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

def check_token_plus(self, database_url, path, access_token=None):
        if access_token:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, access_token)
        else:
            return '{0}{1}.json?access_token={2}'.format(database_url, path, get_firebase_access_token())

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

pyrebase.pyrebase.Database.build_request_url = build_request_url_plus
pyrebase.pyrebase.Database.check_token = check_token_plus
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
app = Flask(__name__, instance_relative_config=True)
secret_key = get_random_string(10)
session = {}
app.secret_key = bytes(secret_key, 'utf-8')
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

test_config=None


if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

def config_app():
    if not listener.is_alive():
        listener.start()
        app.logger.debug("Started Listener")

    return app

####################################################################################################
# _______________________________________END OF APP CONFIG_________________________________________#
# __________________________________START OF USER AUTHENTICATIONS__________________________________#
####################################################################################################


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
            email = request.form['name']
            session['email'] = email
            password = request.form['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']
                session['usr'] = user_id
                # template_returned = home()
                return redirect('home')
            except Exception as e:
                app.logger.debug(e)
                unsuccessful = 'Please check your credentials'
                return render_template('login.html', umessage=unsuccessful)
    return render_template('login.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
        email = request.form['name']
        auth.send_password_reset_email(email)
        return render_template('login.html')
    return render_template('forgot_password.html')


@app.route('/logout', methods=['GET', 'POST'])
@app.route('/')
def logout():
    auth.current_user = None
    session = {}
    return render_template('login.html')

####################################################################################################
# ___________________________________END OF USER AUTHENTICATIONS___________________________________#
# ________________________________________START OF ZMQ NETWORKING__________________________________#
####################################################################################################

def socket_listener():
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://10.0.3.141:5560")
    sub.setsockopt(zmq.SUBSCRIBE, b'')

    # set up poller
    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)
    while True:
        socks = dict(poller.poll(2))
        if sub in socks and socks[sub] == zmq.POLLIN:
            serialized_message_dict = sub.recv()
            app.logger.debug(serialized_message_dict)
            # Update the string variable

            message_dict = pickle.loads(serialized_message_dict)
            db.child("breakthrough-listen-sandbox").child("flask_vars").child("sub_message").set(message_dict)
            if message_dict["done"] == True:
                time_stamp = time.time()*1000
                algo_type = message_dict["algo_type"]
                message_dict["timestamp"]= time_stamp
                target_name = message_dict["target"]
                db.child("breakthrough-listen-sandbox").child("flask_vars").child('processed_observations').child(algo_type).child(target_name).set(message_dict, firebase_secret_token)
            else:
                algo_type = message_dict["algo_type"]
                url = message_dict["url"]

                db.child("breakthrough-listen-sandbox").child("flask_vars").child('observation_status').child(algo_type).child(url).set(message_dict, firebase_secret_token)
            app.logger.debug(f'Updated database with {message_dict}')
        time.sleep(1)

@app.route('/result')
def hits_form():
    return render_template('zmq_sub.html')

@app.route('/result', methods=['GET', 'POST'])
def zmq_sub():
    alert = ""
    message_dict = {}
    try:
        hits = int(request.form['hits'])
        message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("processed_observations").child("Energy-Detection").order_by_child("timestamp").limit_to_last(hits).get().val()
        sample_urls = {}
        for key in message_dict:
            sample_urls[key] = get_processed_hist_and_img(message_dict[key]["object_uri"]+"/info_df.pkl")
    except:
        alert="invalid number"
    return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict, alert = alert, sample_urls = sample_urls )

@app.route('/trigger')
def my_form():
    try:
        print(session['usr'])
        message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child("Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
        return render_template('zmq_push.html', message_sub=message_dict)
    except KeyError:
        return redirect('login')


@app.route('/trigger', methods=['GET', 'POST'])
def zmq_push():
    try:
        print(session['usr'])
        target_ip = request.form['target_ip']
        message = request.form['message']
        app.logger.debug(str(target_ip))
        app.logger.debug(message)
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.connect(str(target_ip))
        socket.send_pyobj({"message": message})
        message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child("Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
        return render_template('zmq_push.html',  message_sub=message_dict)
    except KeyError:
        return redirect('login')

listener = threading.Thread(target=socket_listener, args=())

####################################################################################################
# _______________________________________END OF ZMQ PIPELINE_______________________________________#
# ________________________________________START OF HOME PAGE____________________________________#
####################################################################################################
def get_uri(bucket_name):
    storage_client = storage.Client("BL-Scale")
    bucket=storage_client.get_bucket(bucket_name)
    print(bucket)
    # List blobs iterate in folder
    blobs=bucket.list_blobs()

    uris = []
    for blob in blobs:
        if "info_df.pkl" in blob.name:
            uris += ["gs://"+bucket_name+"/"+blob.name]
    return uris

def get_observation(uri_str):
    obs = re.search(r"([A-Z])\w+(\+\w+)*", uri_str)
    return obs.group(0)

def get_img_url(df, observation):
    indexes = []
    samples_url = []
    blockn = []
    for row in df.itertuples():
        indexes += [row[1]]
        blockn += [row[4]]
    for i in range(0, len(indexes)):
            samples_url += ["https://storage.cloud.google.com/bl-scale/"+observation+"/filtered/"+str(blockn[i])+"/"+str(indexes[i])+".png"]
    return samples_url
def get_base64_images(observation_name):
    # downloads the best_hits.npy file from the observation bucket
    if path.exists(observation_name + "_best_hits.npy"):
        print("Files already downloaded")
    else:
        utils.download_blob("bl-scale", observation_name + "/best_hits.npy", observation_name + "_best_hits.npy")
    img_array = np.load(observation_name + "_best_hits.npy")
    base64_images = []
    for i in np.arange(0, img_array.shape[0]):
        rawBytes = io.BytesIO()
        plt.imsave(rawBytes,arr=img_array[i], cmap="viridis")
        rawBytes.seek(0)  # return to the start of the file
        pic_hash = base64.b64encode(rawBytes.read())
        img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
        base64_images += [img]
    return base64_images

def get_base64_hist(df):
    plt.style.use("dark_background")
    plt.figure(figsize=(8,6))
    plt.hist(df["freqs"], bins = np.arange(min(df["freqs"]),max(df["freqs"]), 0.8116025973))
    plt.title("Histogram of Hits")
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Count")
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img

#returns dataframe of 3*n filtered images
def filter_images(df, n):
    #filter 1000 to 1400 freqs
    freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
    freq_1000_1400 = freq_1000_1400.sort_values("statistic", ascending=False).head(n)

    #filter 1400 to 1700 freqs
    freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
    freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)

    #filter 1700 plus freqs
    freq_1700 = df[df["freqs"] > 1700]
    freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)

    extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
    return extr_all

# returns list of base64 string hist for first element, list of string image
# urls for the second element. Intakes a string uri
def get_processed_hist_and_img(single_uri):
    data = pd.read_pickle(single_uri)
    observ = get_observation(single_uri)
    processed_data = filter_images(data, 4)
    #return [get_base64_hist(data), get_img_url(processed_data, observ)]
    return [get_base64_hist(data), get_base64_images(observ)]




@app.route('/home', methods=['GET', 'POST'])

def home():
    try:
        print(session['usr'])

        #NOT SURE IF WE NEED THIS YET
        
        #string list of pickles 'gs://bl-scale/GBT_58010_50176_HIP61317_fine/info_df.pkl' excluded
        # uris = ['gs://bl-scale/GBT_58452_79191_HIP115687_fine/info_df.pkl','gs://bl-scale/GBT_58452_78532_HIP115673_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_77868_HIP115570_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_74835_HIP117779_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_75833_HIP117150_fine/info_df.pkl']

        #returns string observation
        

        #returns string list of urls
        

        # takes in string observation name (the key), returns list of base64 strings
        
        #return base64 string of histogram
        

        #returns dataframe of 3*n filtered images
        

        # returns list of base64 string hist for first element, list of string image
        # urls for the second element. Intakes a string uri
        

        # global cache

        # db_cache_keys = []
        # retrieve_cache = db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").get()
        # for rc in retrieve_cache.each():
        #     db_cache_keys += [str(rc.key())]
        # print(db_cache_keys)

        # if not cache:
        #     print("cache empty")
        #     for uri in uris:
        #         observ = get_observation(uri)
        #         cache[observ] = get_processed_hist_and_img(uri)
        #         db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").child(observ).set(cache[observ])
        # else:
        #     if all(db_k in cache.keys() for db_k in db_cache_keys):
        #         print("cache all updated")
        #     else:
        #         print("adding additional to cache")
        #         for db_k in db_cache_keys:
        #             if db_k not in cache.keys():
        #                 for uri in uris:
        #                     if get_observation(uri) == db_k:
        #                         cache[db_k] = get_processed_hist_and_img(uri)
        #                         db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").child(db_k).set(cache[db_k])
        # print("returning home")
        return render_template("home.html", title="Main Page", sample_urls=cache, email = session['email'])#sample_urls=obs_filtered_url, plot_bytes=base64_obs)

    except KeyError:
        return redirect('login')

    def get_cache():
        return cache


import monitor
app.register_blueprint(monitor.bp)

if __name__ == '__main__':
    p1 = threading.Thread(target=socket_listener, args=())
    p1.start()
    app.run()