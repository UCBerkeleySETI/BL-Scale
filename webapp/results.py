
from flask import (Blueprint, render_template, request, redirect, session, Flask)

from main import get_query_firebase, app
from utils import process_message_dict

bp = Blueprint('result', __name__, url_prefix='/result')

@bp.route('/')
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
@bp.route('/', methods=['GET', 'POST'])
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
