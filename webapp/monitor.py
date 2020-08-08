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
from datetime import datetime
from flask import (
    Blueprint, render_template
)
TIME =20

firebase, db = pyrebase_cred_wrapper()

bp = Blueprint('monitor', __name__, url_prefix='/monitor')


@bp.route('/')
def base():
    front_end_data = db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").get().val()
    return render_template("monitor.html", title="Monitor", encoded = front_end_data, time=str(datetime.now())  )
