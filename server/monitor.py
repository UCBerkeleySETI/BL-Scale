from kubernetes import client, config
import zmq
import time
import os
import numpy as np
import collections
import logging
import sys
import pickle
import json
import pprint

from server.utils import get_pod_data, extract_metrics
from shared.db import pyrebase_cred_wrapper
import shared.utils as sutils

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
firebase, db = pyrebase_cred_wrapper()


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
            if key not in data or "CPU" not in data[key] or "RAM" not in data[key]:
                data[key] = collections.defaultdict(dict)
                data[key]["CPU"] = []
                data[key]["RAM"] = []
            # If there is nothing from before we pad it with zeros
            if len(data[key]["CPU"]) < TIME or len(data[key]["CPU"]) < TIME:
                logging.debug("padding zeroes")
                data[key]["CPU"] = sutils.fill_zeros(data[key]["CPU"], TIME)
                data[key]["RAM"] = sutils.fill_zeros(data[key]["RAM"], TIME)
            # Appends the new updated values based on percentages
            data[key]["CPU"].append(np.round((update[key]["CPU"]/total_CPU)*100, decimals=2))
            data[key]["RAM"].append(np.round((update[key]["RAM"]/total_RAM)*100, decimals=2))
            # app.logger.debug('Finished appending values')
            # Pop the old values keeping
            while len(data[key]["CPU"]) > TIME:
                data[key]["CPU"].pop(0)
            while len(data[key]["RAM"]) > TIME:
                data[key]["RAM"].pop(0)

            # commented out
            #image_encode = sutils.get_base64_hist_monitor(
                #list_cpu=data[key]["CPU"], list_ram=data[key]["RAM"], threshold=TIME)

            # app.logger.debug('BASE64 DONE')
            temp_dict["CPU"] = data[key]["CPU"]
            temp_dict["RAM"] = data[key]["RAM"]
            if 'STATUS' in data[key]:
                temp_dict['STATUS'] = data[key]['STATUS']

            # Commented out to avoid storing images in Firebase
            #temp_dict["encode"] = image_encode

            front_end_data[key] = temp_dict
    for key in data:
        if key not in front_end_data:
            front_end_data[key] = data[key]
    # push the updates to the firebase flask variable
    db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").update(front_end_data)
    logging.debug('Updated database WITH MONITOR')


def update_status_messages(status_dict):
    key = status_dict['pod_id']
    if status_dict['IDLE']:
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").child(key).child("STATUS").set("IDLE")
    else:
        db.child("breakthrough-listen-sandbox").child("flask_vars").child("monitor").child(key).child("STATUS").set("ACTIVE")


logging.info("Running")

context = zmq.Context()

broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")

sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://10.0.3.141:5560")
sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

poller = zmq.Poller()
poller.register(sub_socket, zmq.POLLIN)

# set up kubernetes client

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

# start up check
logging.info("Listing pods with their IPs:")
v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    logging.info("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

api_client = client.ApiClient()


pod_data, pod_specs = get_pod_data(api_client, v1)
metrics = extract_metrics(pod_data, pod_specs)
logging.info(json.dumps(metrics, indent=2))

last_broadcast_time = int(time.time())


while True:
    # get metrics from cluster
    current_time = int(time.time())
    if current_time % 30 == 0 and current_time != last_broadcast_time:
        pod_data, pod_specs = get_pod_data(api_client, v1)
        metrics = extract_metrics(pod_data, pod_specs)

        # broadcast from socket
        broadcast_socket.send_multipart([b"METRICS", pickle.dumps(metrics)])
        logging.info(json.dumps(metrics, indent=2))
        last_broadcast_time = current_time

    # log messages received through proxy
    socks = dict(poller.poll(2))
    if sub_socket in socks and socks[sub_socket] == zmq.POLLIN:
        topic, message = sub_socket.recv_multipart()
        logging.info(f"Received message in topic {topic}")
        logging.info(json.dumps(pickle.loads(message), indent=2))
    if int(time.time()) % 60 == 0:
        logging.debug("Polling")
        logging.debug(pprint.pformat(socks))
    if sub_socket in socks and socks[sub_socket] == zmq.POLLIN:
        topic, serialized = sub_socket.recv_multipart()
        if topic == b"MESSAGE":
            serialized_message_dict = serialized
            logging.debug(serialized_message_dict)
            # Update the string variable
            message_dict = pickle.loads(serialized_message_dict)
            logging.debug(f"Received message: {message_dict}")
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
            logging.debug(f'Updated database with {message_dict}')
        if topic == b"METRICS":
            monitoring_serialized = serialized
            monitoring_dict = pickle.loads(monitoring_serialized)
            logging.debug(monitoring_dict)
            # Runs the update monitor function which then pushes updates to the firebase.
            # This is then pulled by the monitor script once its called.
            update_monitor_data(monitoring_dict)
        if topic == b"STATUS":
            status_serialized = serialized
            status_dict = pickle.loads(status_serialized)
            logging.debug(f"status serialized: {status_dict}")
            update_status_messages(status_dict)
