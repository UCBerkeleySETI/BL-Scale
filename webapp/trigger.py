import zmq
from flask import (Blueprint, render_template, current_app, request, redirect, session, Flask)

from main import get_query_firebase, db

import collections

from utils import process_message_dict

bp = Blueprint('trigger', __name__, url_prefix='/trigger')

@bp.route('/')
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
        current_app.logger.debug(e)
        print("returning to login")
        return redirect('../login')


@bp.route('/', methods=['GET', 'POST'])
def zmq_push():
    try:
        if session['token'] is not None:
            compute_request = {}
            for key in request.form:
                compute_request[key] = request.form[key]
            current_app.logger.debug(compute_request)
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
        current_app.logger.debug(e)
        print("returning to login")
        return redirect('../login')
