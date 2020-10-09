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


while True:
    # get metrics from cluster
    pod_data, pod_specs = get_pod_data(api_client, v1)
    metrics = extract_metrics(pod_data, pod_specs)

    # broadcast from socket
    broadcast_socket.send_multipart([b"METRICS", pickle.dumps(metrics)])
    logging.info(json.dumps(metrics, indent=2))

    # sleep 30 seconds
    time.sleep(30)
