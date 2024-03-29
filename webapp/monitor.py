import functools
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import base64
import io
import zmq
import pickle
import time
from db import pyrebase_cred_wrapper
import pyrebase
from firebase_admin import auth
import firebase_admin
import pprint
from collections import OrderedDict
from datetime import datetime
from flask import (
    Blueprint, render_template, current_app
)
TIME = 20
# Calls the firebase credentials and gives back the firebase objects to make http requests
firebase, db = pyrebase_cred_wrapper()

bp = Blueprint('monitor', __name__, url_prefix='/monitor')

#  Monitor page routing


@bp.route('/')
def base():
    # Pulls from the firebase stored values for the monitor
    front_end_data = db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").get().val()

    for key in front_end_data:
        image_encode = sutils.get_base64_hist_monitor(
                list_cpu=front_end_data[key]["CPU"], list_ram=front_end_data[key]["RAM"], threshold=TIME)
        front_end_data[key]["encode"] = image_encode

    current_app.logger.debug(front_end_data.keys())
    front_end_data = clean_metrics(front_end_data)
    # Passes in the time to show when the page was last updated.
    return render_template("monitor.html", title="Monitor", encoded=front_end_data, time=str(datetime.now()))


def clean_metrics(metrics):
    return OrderedDict([(pod, pod_metrics) for pod, pod_metrics in metrics.items()
                        if ("CPU" in pod_metrics and "RAM" in pod_metrics and "STATUS" in pod_metrics)])
