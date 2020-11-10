import monitor
import datetime
from os import path
import os.path
import utils
import firebase_admin
from firebase_admin import auth
from db import pyrebase_cred_wrapper
from flask import (render_template, request, redirect, session, Flask)
from flask_session import Session
import os
import ast
import base64
import collections
import io
import json
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import zmq
import time
import pickle
import logging
import threading
import random
import string
import pprint
global cache


cache = {}

compute_service_address = "tcp://34.66.198.113:5555"
dev_service_address = "tcp://34.122.126.21:5555"


firebase, db = pyrebase_cred_wrapper()
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

# Renders main page


@app.route('/')
@app.route('/index')
def index():
    # Renders the index page
    return render_template('index.html')

# Login function

import traceback
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        email = request.form['name']
        password = request.form['password']
        try:
            # Tries to log user in and if the password and user name fails
            # User is thrown back to login page without a redirect
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user
            session['email'] = email
            session['token'] = user['idToken']
            session['server'] = compute_service_address
            print("completed logging in " + session['token'])
            return redirect('/home')
        except Exception as e:
            app.logger.debug(e)
            traceback.print_exc()
            # Login failed and message is passed onto the front end
            unsuccessful = 'Please check your credentials'
            return render_template('login.html', umessage=unsuccessful)
    return render_template('login.html')

# User forgets password lets user reset


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
        email = request.form['name']
        # Firebase is triggered to check if the email exists
        # Sends an auth to reset the password via an email.
        auth.send_password_reset_email(email)
        return render_template('login.html')
    return render_template('forgot_password.html')

# Logout function


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print("passed through")
    # deletes the session token that is used to check if the user is logged in
    # session token should print None
    session['token'] = None
    print(session['token'])
    auth.current_user = None
    return render_template('login.html')

####################################################################################################
# ___________________________________END OF USER AUTHENTICATIONS___________________________________#
# ________________________________________START OF ZMQ NETWORKING__________________________________#
####################################################################################################

# Creates base64 encoding of the health of CPU and Ram


def get_base64_hist_monitor(list_cpu, list_ram, threshold):
    # Create the x axis for plot
    x = np.arange(len(list_cpu))
    # Use the dark theme plots
    plt.style.use("dark_background")
    plt.figure(figsize=(8, 6))
    # Plot the ram and the cpu list
    plt.plot(x, list_cpu)
    plt.plot(x, list_ram)
    # Labels
    plt.title("Health")
    plt.xlabel("Time")
    plt.ylabel("Percent Usage % ")
    plt.legend(['CPU', 'MEMORY'], loc='upper left')
    # Convert image into bytes
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    # Close plots to save memory
    plt.close("all")
    pic_IObytes.seek(0)
    # Convert to base 64
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img

#  Function to fill list with zeros to initialize a pod's health


def fill_zeros(array, length):
    array = ([0] * (length - len(array))) + array
    return array

# Update the monitored data with the results from firebase flask variables


def update_monitor_data(update, TIME=20):
    front_end_data = {}
    data = db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").get().val()
    if not data:
        data = {}
    for key in update:
        # Only displays the bl-scale-algo pods
        if key.startswith("bl-scale-algo"):
            temp_dict = {}
            # app.logger.debug('appending values')

            total_CPU = update[key]["CPU_REQUESTED"]
            total_RAM = update[key]["RAM_REQUESTED"]
            if key not in data:
                data[key] = collections.defaultdict(dict)
                data[key]["CPU"] = []
                data[key]["RAM"] = []
            # If there is nothing from before we pad it with zeros
            if len(data[key]["CPU"]) < TIME or len(data[key]["CPU"]) < TIME:
                app.logger.debug("padding zeroes")
                data[key]["CPU"] = fill_zeros(data[key]["CPU"], TIME)
                data[key]["RAM"] = fill_zeros(data[key]["RAM"], TIME)
            # Appends the new updated values based on percentages
            data[key]["CPU"].append(np.round((update[key]["CPU"]/total_CPU)*100, decimals=2))
            data[key]["RAM"].append(np.round((update[key]["RAM"]/total_RAM)*100, decimals=2))
            # app.logger.debug('Finished appending values')
            # Pop the old values keeping
            while len(data[key]["CPU"]) > TIME:
                data[key]["CPU"].pop(0)
            while len(data[key]["RAM"]) > TIME:
                data[key]["RAM"].pop(0)
            image_encode = get_base64_hist_monitor(
                list_cpu=data[key]["CPU"], list_ram=data[key]["RAM"], threshold=TIME)
            # app.logger.debug('BASE64 DONE')
            temp_dict["CPU"] = data[key]["CPU"]
            temp_dict["RAM"] = data[key]["RAM"]
            if 'STATUS' in data[key]:
                temp_dict[key]['STATUS'] = data[key]['STATUS']
            temp_dict["encode"] = image_encode
            front_end_data[key] = temp_dict
    for key in data:
        if key not in front_end_data:
           front_end_data[key] = data[key]
    # push the updates to the firebase flask variable
    db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").update(front_end_data)
    app.logger.debug('Updated database WITH MONITOR')

#  Socket listener that runs on a seperate thread

def update_status_messages(status_dict):
    key = status_dict['pod_id']
    if status_dict['IDLE']:
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").child(key).child("STATUS").set("IDLE")
    else:
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").child(key).child("STATUS").set("ACTIVE")


def socket_listener():
    context = zmq.Context()
    # First socket listens to proxy publisher
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect("tcp://10.0.3.141:5560")
    sub_socket.setsockopt(zmq.SUBSCRIBE, b'')

    # set up poller
    poller = zmq.Poller()
    poller.register(sub_socket, zmq.POLLIN)
    while True:
        socks = dict(poller.poll(2))
        if int(time.time()) % 60 == 0:
            app.logger.debug("Polling")
            app.logger.debug(pprint.pformat(socks))
            time.sleep(1)
        if sub_socket in socks and socks[sub_socket] == zmq.POLLIN:
            topic, serialized = sub_socket.recv_multipart()
            if topic == b"MESSAGE":
                serialized_message_dict = serialized
                app.logger.debug(serialized_message_dict)
                # Update the string variable
                message_dict = pickle.loads(serialized_message_dict)
                app.logger.debug(f"Received message: {message_dict}")
                # Adds message to the firebase variables
                db.child("breakthrough-listen-sandbox").child("flask_vars").child("sub_message").set(message_dict)
                if message_dict["done"]:
                    time_stamp = time.time()*1000
                    algo_type = message_dict["algo_type"]
                    message_dict["timestamp"] = time_stamp
                    target_name = message_dict["target"]
                    # Updates the completed observation status and metrics
                    db.child("breakthrough-listen-sandbox").child("flask_vars").child(
                        'processed_observations').child(algo_type).child(target_name).set(message_dict)
                else:
                    algo_type = message_dict["algo_type"]
                    url = message_dict["url"]
                    # Updates the observation status
                    db.child("breakthrough-listen-sandbox").child("flask_vars").child(
                        'observation_status').child(algo_type).child(url).set(message_dict)
                app.logger.debug(f'Updated database with {message_dict}')
            if topic == b"METRICS":
                monitoring_serialized = serialized
                monitoring_dict = pickle.loads(monitoring_serialized)
                app.logger.debug(monitoring_dict)
                # Runs the update monitor function which then pushes updates to the firebase.
                # This is then pulled by the monitor script once its called.
                update_monitor_data(monitoring_dict)
            if topic == b"STATUS":
                status_serialized = serialized
                status_dict = pickle.loads(status_serialized)
                app.logger.debug(f"status serialized: {status_dict}")
                update_status_messages(status_dict)


def get_query_firebase(num):
    # Gets a query for the observations from energy detection based on a certain number
    message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("processed_observations").child(
        "Energy-Detection").order_by_child("timestamp").limit_to_last(num).get().val()
    # Mutating the dictionary within the loop and needs a deep copy
    copy_of_dict = message_dict.copy()
    message_dict = collections.OrderedDict(reversed(list(message_dict.items())))
    for index in message_dict.items():
        # getting rid of mid resolution files
        print("getting rid of mid res " + str(index[0]))
        if "mid" in str(index[0]):
            print("deleting")
            del copy_of_dict[index[0]]

    db_cache_keys = []
    print("got query")
    # Storing the files in the firebase flask variable "cache"
    retrieve_cache = db.child(
        "breakthrough-listen-sandbox").child("flask_vars").child("cache").get()
    for rc in retrieve_cache.each():
        db_cache_keys += [str(rc.key())]

    for key in copy_of_dict:
        # Creates the Base64 encode of the values and pushes it to the firebase.
        cache[key] = get_processed_hist_and_img(copy_of_dict[key]["object_uri"]+"/info_df.pkl")
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("cache").child(key).set(cache[key])
    return copy_of_dict, cache


def convert_time_to_datetime(dict, time_stamp_key="start_timestamp"):
    # Helps convert the timestamp values in Milliseconds since Epoch to readable date time string.
    for k in dict:
        if time_stamp_key in dict[k]:
            temp = dict[k][time_stamp_key]
            temp = temp/1000
            date_time = datetime.datetime.fromtimestamp(temp).strftime('%c')
            dict[k][time_stamp_key] = date_time
    return dict

# Rounding values from the dictionary


def round_processing_time(dict):
    for obs in dict:
        if "processing_time" in dict[obs]:
            dict[obs]["processing_time"] = np.round(dict[obs]["processing_time"] / 60, decimals=2)
    return dict

# Includes rounding of time and converting timestamp to a date.


def process_message_dict(message_dict, time_stamp_key="start_timestamp"):
    message_dict = convert_time_to_datetime(message_dict, time_stamp_key=time_stamp_key)
    message_dict = round_processing_time(message_dict)
    for obs in message_dict:
        if "filename" not in message_dict[obs]:
            message_dict[obs]["filename"] = message_dict[obs]["url"]
    return message_dict

# Display the default results page.


@app.route('/result')
def hits_form():
    global cache
    session["results_counter"] = 1
    try:
        # Check if the user is logged in
        if session['token'] is not None:
            # Query the last 3 results
            message_dict, cache = get_query_firebase(3)
            # Make plots for the queried results
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            # Push them to front end
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict, sample_urls=cache, test_login=True)
        else:
            message_dict, cache = get_query_firebase(3)
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict, sample_urls=cache, test_login=False)
    except Exception as e:
        # If user isn't logged in we show a different UI
        app.logger.debug(e)
        message_dict, cache = get_query_firebase(3)
        message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
        return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls=cache, test_login=False)


# Request to add 3 more
@app.route('/result', methods=['GET', 'POST'])
def zmq_sub():
    global cache
    print("adding 3 more images")
    # Added 3 more token incremented
    try:
        if session['token'] is not None:
            message_dict = {}
            # Increase the counter
            session["results_counter"] += 1
            # Request for 3 more
            message_dict, cache = get_query_firebase(3*session["results_counter"])
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls=cache, test_login=True)
        else:
            session["results_counter"] += 1
            message_dict, cache = get_query_firebase(3*session["results_counter"])
            message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
            return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict,  sample_urls=cache, test_login=False)
    except Exception as e:
        app.logger.debug(e)
        # add three function for not logged in users.
        message_dict, cache = get_query_firebase(3*session["results_counter"])
        message_dict = process_message_dict(message_dict, time_stamp_key="timestamp")
        return render_template("zmq_sub.html", title="Main Page", message_sub=message_dict, sample_urls=cache, test_login=False)

@app.route('/poll')
def poll():

    # client_state = ast.literal_eval(request.args.get("state"))
    last_state = session.get("trigger_state", {})

    #poll the database
    while True:
        try:
            app.logger.debug("polling for triggers")
            time.sleep(1)
            if session['token'] is not None:
                # Gets the most recent triggers from the observation status variables
                message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child(
                    "Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
                # we want the order of the most recent triggers to be from most recent to least recent
                message_dict = collections.OrderedDict(reversed(list(message_dict.items())))
                # Gets the results and forms the time
                message_dict = process_message_dict(message_dict)
                if message_dict != last_state:
                    print("client_state", type(last_state))
                    session["trigger_state"] = message_dict
                    return "change"
                else:
                    return "Same"
            else:
                raise RuntimeError("Need to login")
        except Exception as e:
            app.logger.info(f"Exception encountered: {e}")
            raise RuntimeError("Need to login")

@app.route('/toggle-server')
def toggleServer():
    if session["server"] == compute_service_address:
        session["server"] = dev_service_address
        return "development"
    else:
        session["server"] = compute_service_address
        return "production"



@app.route('/trigger')
def my_form():
    try:
        if session['token'] is not None:
            print("get querry, trigger")
            # Gets the most recent triggers from the observation status variables
            message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child(
                "Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
            print("Convert time")
            # we want the order of the most recent triggers to be from most recent to least recent
            message_dict = collections.OrderedDict(reversed(list(message_dict.items())))
            # Gets the results and forms the time
            message_dict = process_message_dict(message_dict)
            return render_template('zmq_push.html', message_sub=message_dict)
        else:
            print("no session token")
            return redirect('../login')
    except Exception as e:
        app.logger.debug(e)
        print("returning to login")
        return redirect('../login')


@app.route('/trigger', methods=['GET', 'POST'])
def zmq_push():
    try:
        if session['token'] is not None:
            compute_request = {}
            for key in request.form:
                compute_request[key] = request.form[key]
            app.logger.debug(compute_request)
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect(session["server"])
            socket.send_pyobj(compute_request)
            # keys are "alg_package", "alg_name", and "input_file_url"
            message_dict = db.child("breakthrough-listen-sandbox").child("flask_vars").child("observation_status").child(
                "Energy-Detection").order_by_child("start_timestamp").limit_to_last(3).get().val()
            # we want the order of the most recent triggers to be from most recent to least recent
            message_dict = collections.OrderedDict(reversed(list(message_dict.items())))
            message_dict = process_message_dict(message_dict)
            return render_template('zmq_push.html',  message_sub=message_dict)
        else:
            return redirect('../login')
    except Exception as e:
        app.logger.debug(e)
        print("returning to login")
        return redirect('../login')


listener = threading.Thread(target=socket_listener, args=())

####################################################################################################
# _______________________________________END OF ZMQ PIPELINE_______________________________________#
# ________________________________________START OF Notebook PAGE____________________________________#
####################################################################################################

# Note book menu page


@app.route('/BL-Reservoir', methods=['GET', 'POST'])
def algo_menu():
    return render_template('algo_menu.html')

# Render notebook holder


@app.route('/energy_detection_notebook', methods=['GET', 'POST'])
def energy_detection_notebook():
    return render_template('energy_detection_wrapper.html')

# Render the iframe for the notebook


@app.route('/energydetection_notebook/seti-energy-detection.html')
def energy_detection_iframe():
    return render_template('./energydetection_notebook/seti-energy-detection.html')
####################################################################################################
# _______________________________________END OF Notebook PAGE_______________________________________#
# ________________________________________START OF HOME PAGE____________________________________#
####################################################################################################

# Intakes a string uri taken from the file on GCP
# Returns the string observation name


def get_observation(uri_str):
    obs = re.search(r"([A-Z])\w+(\+\w+)*", uri_str)
    return obs.group(0)

# Intakes a pandas dataframe and string observation name
# Returns a list of image urls
# Use get_base64_images(observation_name) function instead of this


def get_img_url(df, observation):
    indexes = []
    samples_url = []
    blockn = []
    for row in df.itertuples():
        indexes += [row[1]]
        blockn += [row[4]]
    for i in range(0, len(indexes)):
        samples_url += ["https://storage.cloud.google.com/bl-scale/" +
                        observation+"/filtered/"+str(blockn[i])+"/"+str(indexes[i])+".png"]
    return samples_url


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

# Intakes a string observation name
# Returns the base64 string of the images (use this for the images on the results page)


def get_base64_images(observation_name):
    # checks to see if you already have the file, else
    # downloads the best_hits.npy file from the observation bucket
    if path.exists(observation_name + "_best_hits.npy"):
        print("Files already downloaded")
    else:
        utils.download_blob("bl-scale", observation_name + "/best_hits.npy",
                            observation_name + "_best_hits.npy")
    img_array = np.load(observation_name + "_best_hits.npy")
    base64_images = {}
    for i in np.arange(0, img_array.shape[0]):
        key = get_random_string(6)
        rawBytes = io.BytesIO()
        plt.imsave(rawBytes, arr=img_array[i], cmap="viridis")
        rawBytes.seek(0)  # return to the start of the file
        pic_hash = base64.b64encode(rawBytes.read())
        img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
        base64_images[key] = img
    return base64_images

# Intakes a pandas dataframe
# Returns a base64 image of the generated histogram of frequence distribution


def get_base64_hist(df):
    plt.style.use("dark_background")
    plt.figure(figsize=(8, 6))
    plt.hist(df["freqs"], bins=np.arange(min(df["freqs"]), max(df["freqs"]), 0.8116025973))
    plt.title("Histogram of Hits")
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Count")
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img

# Returns dataframe of 3*n filtered images with the most extreme s-values


def filter_images(df, n):
    # filter 1000 to 1400 freqs
    freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
    freq_1000_1400 = freq_1000_1400.sort_values("statistic", ascending=False).head(n)

    # filter 1400 to 1700 freqs
    freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
    freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)

    # filter 1700 plus freqs
    freq_1700 = df[df["freqs"] > 1700]
    freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)

    extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
    return extr_all

# returns list of base64 string hist for first element, list of string image
# urls for the second element. Intakes a string uri


def get_processed_hist_and_img(single_uri):
    try:
        data = pd.read_pickle(single_uri)
        observ = get_observation(single_uri)
        return [get_base64_hist(data), get_base64_images(observ)]
    except:
        print("could not find file "+ single_uri)

# Dashboard page and displays the cards


@app.route('/home', methods=['GET', 'POST'])
def home():
    # Checks if user is logged in
    try:
        if session['token'] is not None:
            print("entering home")
            app.logger.debug(session['user'])
            # Add in email to front end to display
            return render_template("home.html", email=session['email'], title="Main Page")
        else:
            # Redirect to login page if user isn't logged in
            return redirect('../login')
    except Exception as e:
        app.logger.debug(e)
        return redirect('../login')


@app.route('/test_counter')
def counter():
    session["counter"] = session.get("counter", 0) + 1
    return str(session["counter"])


app.register_blueprint(monitor.bp)

if __name__ == '__main__':
    app = config_app()
    app.run()
