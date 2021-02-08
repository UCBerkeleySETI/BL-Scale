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
    current_app.logger.debug(front_end_data)
    # Passes in the time to show when the page was last updated.
    return render_template("monitor.html", title="Monitor", encoded=front_end_data, time=str(datetime.now()))
