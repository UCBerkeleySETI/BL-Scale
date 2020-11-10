from kubernetes import client, config
import zmq
import time
import os
import logging
import sys
import pickle
import json
from utils import get_pod_data, extract_metrics

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logging.info("Running")

context = zmq.Context()

broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")

logging_socket = context.socket(zmq.SUB)
logging_socket.connect("tcp://10.0.3.141:5560")
logging_socket.setsockopt(zmq.SUBSCRIBE, b"")

poller = zmq.Poller()
poller.register(logging_socket, zmq.POLLIN)

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
    poll_data = dict(poller.poll(2))
    if logging_socket in poll_data and poll_data[logging_socket] == zmq.POLLIN:
        topic, message = logging_socket.recv_multipart()
        logging.info(f"Received message in topic {topic}")
        logging.info(json.dumps(pickle.loads(message), indent=2))
