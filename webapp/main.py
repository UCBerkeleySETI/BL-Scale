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
cache = {}
import multiprocessing


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
auth = firebase.auth()
db = firebase.database()
app = Flask(__name__, instance_relative_config=True)

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
        print("Started Listener")

    return app


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
                auth.sign_in_with_email_and_password(email, password)
                template_returned = home()
                return template_returned
            except:
                unsuccessful = 'Please check your credentials'
                return render_template('login.html', umessage=unsuccessful)
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            try:
                auth.create_user_with_email_and_password(email, password)
                return render_template('login.html')
            except:
                unsuccessful = 'Issues with credentials - Cannot sign you up :('
                return render_template('create_account.html', umessage=unsuccessful)
    return render_template('create_account.html')

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
    return render_template('login.html')

####################################################################################################
# ___________________________________END OF USER AUTHENTICATIONS___________________________________#
# ________________________________________START OF ZMQ NETWORKING__________________________________#
####################################################################################################

def get_sub():
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://10.0.3.141:5560")
    sub.setsockopt(zmq.SUBSCRIBE, b'')

    # set up poller
    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)
    while True:
        app.logger.debug("Polling for message")
        socks = dict(poller.poll(2))
        if sub in socks and socks[sub] == zmq.POLLIN:
            serialized_message_dict = sub.recv()
            print(serialized_message_dict)
            # Update the string variable
            message_dict = pickle.loads(serialized_message_dict)
            db.child("breakthrough-listen-sandbox").child("flask_vars").child("sub_message").set(message_dict)
            app.logger.debug('Updated database')
        else:
            app.logger.debug("No message has been received, waiting...")
        time.sleep(1)

@app.route('/zmq_sub', methods=['GET', 'POST'])
def zmq_sub():
    message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("sub_message").get().val()
    if not message_dict:
        message = "No Data From Publisher Node"
        return render_template("zmq_sub.html", title="Main Page", message_sub=message)
    app.logger.debug(f" ---{message_dict}--- getting from webpage")
    if message_dict["message"] == "":
        message = "No Data From Publisher Node"
    else:
        message = message_dict["message"]
    return render_template("zmq_sub.html", title="Main Page", message_sub=message)

@app.route('/zmq_push')
def my_form():
    return render_template('zmq_push.html')

@app.route('/zmq_push', methods=['GET', 'POST'])
def zmq_push():
    target_ip = request.form['target_ip']
    message = request.form['message']
    # print(str(target_ip))
    # print(message)
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(str(target_ip))
    socket.send_pyobj({"message": message})
    return render_template('zmq_push.html')

listener = threading.Thread(target=get_sub, args=())

####################################################################################################
# _______________________________________END OF ZMQ PIPELINE_______________________________________#
# ________________________________________START OF HOME PAGE____________________________________#
####################################################################################################

@app.route('/home', methods=['GET', 'POST'])
def home():
    def get_cache():
        return cache
    #client, request data
    def get_data():
        message_list = []
        context = zmq.Context()
        # Socket to talk to server
        print("Connecting to server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://*:5555")

        for request in range(1):
            print("Sending request %s..." % request)
            socket.send(b"Please send over data")

            # Get the reply
            message = pickle.loads(socket.recv())
            message_list += [message]
        return message_list

    #server, send data
    def send_data(info):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")

        while True:
            # Wait for next request from client
            message = socket.recv()
            print("Request received: %s" % message)

            #D o some 'work'
            time.sleep(1)

            # Send reply back to client
            socket.send(pickle.dumps(info))

    #NOT SURE IF WE NEED THIS YET
    def get_uri(bucket_name):

        #bucket_name = 'bl-scale'

        storage_client = storage.Client("BL-Scale")
        # Retrieve all blobs with a prefix matching the file.
        bucket=storage_client.get_bucket(bucket_name)
        print(bucket)
        # List blobs iterate in folder
        blobs=bucket.list_blobs()

        uris = []
        for blob in blobs:
            if "info_df.pkl" in blob.name:
                uris += ["gs://"+bucket_name+"/"+blob.name]
        return uris

    #string list of pickles 'gs://bl-scale/GBT_58010_50176_HIP61317_fine/info_df.pkl' excluded
    uris = ['gs://bl-scale/GBT_58014_69579_HIP77629_fine/info_df.pkl', 'gs://bl-scale/GBT_58110_60123_HIP91926_fine/info_df.pkl', 'gs://bl-scale/GBT_58202_60970_B0329+54_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_37805_HIP103730_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_39862_HIP105504_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_40853_HIP106147_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_41185_HIP105761_fine/info_df.pkl', 'gs://bl-scale/GBT_58307_26947_J1935+1616_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_79191_HIP115687_fine/info_df.pkl']

    #returns string observation
    def get_observation(uri_str):

        obs = re.search(r"([A-Z])\w+(\+\w+)*", uri_str)
        return obs.group(0)

    #returns string list of urls
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

    #return base64 string of histogram
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
        # std_stat_1000_1400 = np.std(freq_1000_1400["statistic"])
        # extr_1000_1400 = freq_1000_1400[freq_1000_1400["statistic"] >= 8*std_stat_1000_1400]

        #filter 1400 to 1700 freqs
        freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
        freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)
        # std_stat_1400_1700 = np.std(freq_1400_1700["statistic"])
        # extr_1400_1700 = freq_1400_1700[freq_1400_1700["statistic"] >= 7*std_stat_1400_1700]

        #filter 1700 plus freqs
        freq_1700 = df[df["freqs"] > 1700]
        freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)
        # std_stat_1700 = np.std(freq_1700["statistic"])
        # extr_1700 = freq_1700[freq_1700["statistic"] >= 8*std_stat_1700]

        extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
        return extr_all

    #Dictionary, observation name for key, string list of urls for value
    obs_filtered_url = {}
    #Dictionary, observation name for key, string base64 of histogram for value
    base64_obs = {}
    #iterate through every observation dataframe in uri list
    #fills in the obs_filtered_url and base64_obs dictionary to be passed into render_template
    global cache

    if not cache:
        print("cache empty")
        for uri in uris:

            data = pd.read_pickle(uri)

            observ = get_observation(uri)

            base64_obs[observ] = get_base64_hist(data)

            processed_data = filter_images(data, 4)

            obs_filtered_url[observ] = get_img_url(processed_data, observ)
            cache[observ] = [base64_obs[observ], obs_filtered_url[observ]]
    else:
        print("cache not empty")
        for key in cache.keys():
            obs_filtered_url[key] = cache[key][1]
            base64_obs[key] = cache[key][0]
    print("returning home")
    return render_template("home.html", title="Main Page", sample_urls=obs_filtered_url, plot_bytes=base64_obs)

if __name__ == '__main__':
    p1 = threading.Thread(target=get_sub, args=())
    p1.start()
    app.run()
