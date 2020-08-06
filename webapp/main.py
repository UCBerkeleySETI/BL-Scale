import pyrebase
from flask import (render_template, request, redirect, session,
  render_template, request, redirect, Flask, jsonify)
from flask_session import Session
import os
import base64
import collections
import io
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
import time
import os
import threading
global cache
import time
import multiprocessing
import urllib.request, json
from urllib.parse import urlencode, quote
from google.oauth2 import service_account
from firebase_admin import auth
import firebase_admin
import utils
from PIL import Image
import os.path
from os import path
import random
import datetime
import string


cache = {}

compute_service_address = "tcp://34.66.198.113:5555"

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


def check_if_login():
    try:
        print(session['usr'])
        return True
    except KeyError:
        return False

pyrebase.pyrebase.Database.build_request_url = build_request_url_plus
pyrebase.pyrebase.Database.check_token = check_token_plus
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
default_app = firebase_admin.initialize_app()

db = firebase.database()
sess = Session()
app = Flask(__name__, instance_relative_config=False)
app.config.from_object('config.Config')

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')

    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

def config_app():
    sess.init_app(app)
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
            password = request.form['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                session['user'] = user
                session['email'] = email
                session['token'] = user['idToken']
                print("completed logging in "+ session['token'])
                return redirect('/home')
            except:
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
def logout():
    print("passed through")
    session['token'] = None
    print(session['token'])
    auth.current_user = None
    return render_template('login.html')

####################################################################################################
# ___________________________________END OF USER AUTHENTICATIONS___________________________________#
# ________________________________________START OF ZMQ NETWORKING__________________________________#
####################################################################################################
def get_base64_hist_monitor(list_cpu, list_ram, threshold):
    x = np.arange(len(list_cpu))
    plt.style.use("dark_background")
    plt.figure(figsize=(8,6))
    plt.plot(x, list_cpu)
    plt.plot(x, list_ram)
    plt.title("Health")
    plt.xlabel("Time")
    plt.ylabel("Percent Usage % ")
    plt.legend(['CPU', 'MEMORY' ], loc='upper left')
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    plt.close("all")
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img

def fill_zeros(array, length):
    return ([0] * (length - len(array))).extend(array)

def update_monitor_data(update, TIME=20):
    front_end_data = {}
    data = db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").get().val()
    for key in update:
        if key.startswith("bl-scale-algo"):
            temp_dict = {}
            app.logger.debug('appending values')
            total_CPU = update[key]["CPU_REQUESTED"]
            total_RAM = update[key]["RAM_REQUESTED"]
            if key not in data:
                data[key] = collections.defaultdict(dict)
            if len(data[key]["CPU"]) < TIME or len(data[key]["CPU"]) < TIME:
                data[key]["CPU"] = fill_zeros(data[key]["CPU"], TIME)
                data[key]["RAM"] = fill_zeros(data[key]["RAM"], TIME)
            data[key]["CPU"].append(np.round((update[key]["CPU"]/total_CPU)*100), decimals=2)
            data[key]["RAM"].append(np.round((update[key]["RAM"]/total_RAM)*100), decimals=2)
            app.logger.debug('Finished appending values')
            while len(data[key]["CPU"]) > TIME:
                data[key]["CPU"].pop(0)
            while len(data[key]["RAM"]) > TIME:
                data[key]["RAM"].pop(0)
            image_encode = get_base64_hist_monitor(list_cpu=data[key]["CPU"], list_ram=data[key]["RAM"], threshold=TIME)
            app.logger.debug('BASE64 DONE')
            temp_dict["CPU"] = data[key]["CPU"]
            temp_dict["RAM"] = data[key]["RAM"]
            temp_dict["encode"] = image_encode
            front_end_data[key] = temp_dict
            # except:
            #     print("JUST ONLINE")
            #     app.logger.debug('JUST ONLINE')
            #     data[key] = {}
            #     data[key]["CPU"] = fill_zero(TIME)
            #     data[key]["RAM"] = fill_zero(TIME)
            #     app.logger.debug('Appending values')
            #     total_CPU = update[key]["CPU_REQUESTED"]
            #     total_RAM = update[key]["RAM_REQUESTED"]
            #     data[key]["CPU"].append(int(update[key]["CPU"]))
            #     data[key]["RAM"].append(int(update[key]["RAM"])/total_RAM)
            #     app.logger.debug('Finished appending values')
            #     if len( data[key]["CPU"]) >TIME:
            #         data[key]["CPU"].pop(0)
            #     if len( data[key]["RAM"]) >TIME:
            #         data[key]["RAM"].pop(0)
            #     image_encode = get_base64_hist_monitor(list_cpu=data[key]["CPU"], list_ram=data[key]["RAM"],  threshold=TIME )
            #     app.logger.debug('BASE64 DONE')
            #     temp_dict["CPU"] = data[key]["CPU"]
            #     app.logger.debug('CPU UPDATE DONE')
            #     temp_dict["RAM"] = data[key]["RAM"]
            #     app.logger.debug('RAM UPDATE DONE')
            #     temp_dict["encode"] = image_encode
            #     app.logger.debug('ENCODE UPDATE DONE')
            #     front_end_data[key] = temp_dict
            #     app.logger.debug('BUNDLED UPDATE DONE')
    db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").set(front_end_data)
    app.logger.debug('Updated database WITH MONITOR')

def socket_listener():
    context = zmq.Context()
    message_sub_socket  = context.socket(zmq.SUB)
    message_sub_socket .connect("tcp://10.0.3.141:5560")
    message_sub_socket .setsockopt(zmq.SUBSCRIBE, b'MESSAGE')

    monitor_sub_socket  = context.socket(zmq.SUB)
    monitor_sub_socket.connect("tcp://10.0.3.141:5560")
    monitor_sub_socket.setsockopt(zmq.SUBSCRIBE, b'METRICS')

    # set up poller
    poller = zmq.Poller()
    poller.register(message_sub_socket , zmq.POLLIN)
    poller.register(monitor_sub_socket , zmq.POLLIN)
    while True:
        socks = dict(poller.poll(2))
        if int(time.time()) % 60 == 0:
            app.logger.debug("Polling")
        if message_sub_socket  in socks and socks[message_sub_socket ] == zmq.POLLIN:
            serialized_message_dict = message_sub_socket .recv_multipart()[1]
            app.logger.debug(serialized_message_dict)
            # Update the string variable
            message_dict = pickle.loads(serialized_message_dict)
            app.logger.debug(f"Received message: {message_dict}")
            db.child("breakthrough-listen-sandbox").child("flask_vars").child("sub_message").set(message_dict)
            if message_dict["done"] == True:
                time_stamp = time.time()*1000
                algo_type = message_dict["algo_type"]
                message_dict["timestamp"]= time_stamp
                target_name = message_dict["target"]
                db.child("breakthrough-listen-sandbox").child("flask_vars").child('processed_observations').child(algo_type).child(target_name).set(message_dict)
            else:
                algo_type = message_dict["algo_type"]
                url = message_dict["url"]
                db.child("breakthrough-listen-sandbox").child("flask_vars").child('observation_status').child(algo_type).child(url).set(message_dict)
            app.logger.debug(f'Updated database with {message_dict}')

        if monitor_sub_socket in socks and socks[monitor_sub_socket] == zmq.POLLIN:
            monitoring_serialized = monitor_sub_socket.recv_multipart()[1]
            monitoring_dict = pickle.loads(monitoring_serialized)
            app.logger.debug(monitoring_dict)
            update_monitor_data(monitoring_dict)
            app.logger.debug("updated monitor data")
        time.sleep(1)


def get_query_firebase(num):
    message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("processed_observations").child("Energy-Detection").order_by_child("timestamp").limit_to_last(num).get().val()
    db_cache_keys = []
    print("got query")
    retrieve_cache = db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").get()
    for rc in retrieve_cache.each():
        db_cache_keys += [str(rc.key())]
    # print(db_cache_keys)
    for key in message_dict:
        cache[key] = get_processed_hist_and_img(message_dict[key]["object_uri"]+"/info_df.pkl")
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").child(key).set(cache[key])
    return message_dict, cache

def convert_time_to_datetime(dict, time_stamp_key="start_timestamp"):
    for k in dict:
        if time_stamp_key in dict[k]:
                temp = dict[k][time_stamp_key]
                temp = temp/1000
                date_time =  datetime.datetime.fromtimestamp(temp).strftime('%c')
                dict[k][time_stamp_key] = date_time
    return dict

def round_processing_time(dict):
    for obs in dict:
        if "processing_time" in dict[obs]:
            dict[obs]["processing_time"] = np.round(dict[obs]["processing_time"] / 60, decimals=2)
    return dict

def process_message_dict(message_dict, time_stamp_key="start_timestamp"):
    message_dict = convert_time_to_datetime(message_dict, time_stamp_key=time_stamp_key)
    message_dict = round_processing_time(message_dict)
    return message_dict

@app.route('/result')
def hits_form():
    global cache
    session["results_counter"]=1

    try:
        alert = ""
        if session['token'] !=None:
            message_dict, cache = get_query_firebase(3)
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls = cache ,test_login = True)
        else:
            message_dict, cache = get_query_firebase(3)
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls = cache ,test_login = False)
    except:
        message_dict, cache = get_query_firebase(3)
        message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
        return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls = cache ,test_login = False)



@app.route('/result', methods=['GET', 'POST'])
def zmq_sub():
    global cache
    print("adding 3 more images")
    try:
        if session['token'] !=None:
            alert = ""
            message_dict = {}
            session["results_counter"]+=1
            message_dict, cache =get_query_firebase(3*session["results_counter"])
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp" )
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls = cache ,test_login = True)
        else:
            print("trying to get three")
            session["results_counter"]+=1
            message_dict, cache =get_query_firebase(3*session["results_counter"])
            print(cache)
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp" )
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls = cache ,test_login = False)
    except:

        message_dict, cache =get_query_firebase(3*session["results_counter"])
        message_dict = process_message_dict(message_dict, time_stamp_key="timestamp" )
        return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict, sample_urls = cache ,test_login = False)

@app.route('/trigger')
def my_form():
    try:
        if session['token'] !=None:
            print("get querry")
            message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child("Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
            print("Convert time")
            message_dict = process_message_dict(message_dict)
            print("Return")
            return render_template('zmq_push.html', message_sub=message_dict)
        else:
            return redirect('../login')
    except:
        print("returning to login")
        return redirect('../login')


@app.route('/trigger', methods=['GET', 'POST'])
def zmq_push():
    try:
        if session['token']!= None:
            compute_request = {}
            for key in request.form:
                compute_request[key] = request.form[key]
            app.logger.debug(compute_request)
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect(compute_service_address)
            socket.send_pyobj(compute_request)
            # keys are "alg_package", "alg_name", and "input_file_url"
            message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child("Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
            message_dict = process_message_dict(message_dict)
            return render_template('zmq_push.html',  message_sub=message_dict)
        else:
            return redirect('../login')
    except:
        print("returning to login")
        return redirect('../login')


listener = threading.Thread(target=socket_listener, args=())

####################################################################################################
# _______________________________________END OF ZMQ PIPELINE_______________________________________#
# ________________________________________START OF Notebook PAGE____________________________________#
####################################################################################################
@app.route('/BL-Reservoir', methods=['GET', 'POST'])
def algo_menu():
    return render_template('algo_menu.html')

@app.route('/energy_detection_notebook', methods=['GET', 'POST'])
def energy_detection_notebook():
    return render_template('energy_detection_wrapper.html')

@app.route('/energydetection_notebook/seti-energy-detection.html')
def energy_detection_iframe():
    return render_template('./energydetection_notebook/seti-energy-detection.html')
####################################################################################################
# _______________________________________END OF Notebook PAGE_______________________________________#
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
    #checks to see if you already have the file, else
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
    #processed_data = filter_images(data, 4)
    #return [get_base64_hist(data), get_img_url(processed_data, observ)]
    return [get_base64_hist(data), get_base64_images(observ)]




@app.route('/home', methods=['GET', 'POST'])
def home():

    try:
        if session['token'] !=None:
            print("entering home")
            app.logger.debug(session['user'])
            return render_template("home.html",email = session['email'], title="Main Page")
        else:
            return redirect('../login')
    except:
        return redirect('../login')

@app.route('/test_counter')
def counter():
    session["counter"] = session.get("counter", 0) + 1
    return str(session["counter"])


import monitor
app.register_blueprint(monitor.bp)

if __name__ == '__main__':
    app = config_app()
    app.run()
