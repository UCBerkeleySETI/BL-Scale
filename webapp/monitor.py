import functools
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import base64
import io
from db import pyrebase_cred_wrapper
import pyrebase
from firebase_admin import auth
import firebase_admin
from datetime import datetime
from flask import (
    Blueprint, render_template
)
TIME =20

firebase, db = pyrebase_cred_wrapper()

def fill_zero(length):
    y =[]
    for i in range(length-1):
        y.append(0)
    return y
data = {}
bp = Blueprint('monitor', __name__, url_prefix='/monitor')

def get_base64_hist(list_cpu, list_ram, threshold):
    x = np.arange(len(list_cpu))
    plt.style.use("dark_background")
    plt.figure(figsize=(8,6))
    plt.plot(x, list_cpu)
    plt.plot(x, list_ram)
    plt.title("Health")
    plt.xlabel("Time")
    plt.ylabel("Percent % ")
    plt.legend(['CPU', 'MEMORY' ], loc='upper left')
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    plt.cla()
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    
    return base64_img

@bp.route('/')
def base():
    update={
    "pod1":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    },
    "pod2":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    },
    "pod3":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    },
    "pod4":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    },
    "pod5":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    },
    "pod6":{
        "cpu":int(random.random()*100),
        "ram":int(random.random()*100),
        "message":"This is the status of your pod1. This will contain a message about the status of your pods"
    }
    }
    # get data from socket. 
    front_end_data = {}
    data = db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").get().val()
    for key in update:
        temp_dict = {}
        try:
            data[key]["cpu"].append(update[key]["cpu"]) 
            data[key]["ram"].append(update[key]["ram"]) 
            if len( data[key]["cpu"]) >TIME:
                data[key]["cpu"].pop(0)
            if len( data[key]["ram"]) >TIME:
                data[key]["ram"].pop(0)
            image_encode = get_base64_hist( list_cpu =data[key]["cpu"] ,list_ram=data[key]["ram"] ,  threshold = TIME )
            temp_dict["cpu"] = update[key]["cpu"]
            temp_dict["ram"] = update[key]["ram"]
            temp_dict["encode"] = image_encode
            front_end_data[key] = temp_dict
        except:
            print("JUST ONLINE")
            data[key] = {}
            data[key]["cpu"] = fill_zero(TIME)
            data[key]["ram"] = fill_zero(TIME)
            data[key]["cpu"].append(update[key]["cpu"]) 
            data[key]["ram"].append(update[key]["ram"]) 
            if len( data[key]["cpu"]) >TIME:
                data[key]["cpu"].pop(0)
            if len( data[key]["ram"]) >TIME:
                data[key]["ram"].pop(0)
            image_encode = get_base64_hist( list_cpu =data[key]["cpu"] ,list_ram=data[key]["ram"] ,  threshold = TIME )
            temp_dict["cpu"] = update[key]["cpu"]
            temp_dict["ram"] = update[key]["ram"]
            temp_dict["encode"] = image_encode
            front_end_data[key] = temp_dict
    db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").set(data)
    return render_template("monitor.html", title="Monitor", encoded = front_end_data, time=str(datetime.now())  )