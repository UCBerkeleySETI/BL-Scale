import zmq
import time
import os
import logging
import sys
import pickle
import json
from collections import defaultdict

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.info("Running")

context = zmq.Context()

broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")

# set up kubernetes client
from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

# start up check
logging.info("Listing pods with their IPs:")
v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    logging.info("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

api_client = client.ApiClient()
def get_pod_data(api_client):
    ret_metrics = api_client.call_api(
                '/apis/metrics.k8s.io/v1beta1/namespaces/' + 'default' + '/pods', 'GET',
                auth_settings=['BearerToken'], response_type='json', _preload_content=False)
    response = ret_metrics[0].data.decode('utf-8')
    data = json.loads(response)
    return data

def extract_metrics(pod_data):
    pods = pod_data["items"]
    metrics = defaultdict(dict)
    for pod in pods:
        pod_name = pod["metadata"]["name"]
        metrics[pod_name]["CPU"] = pod["containers"][0]["usage"]["cpu"]
        metrics[pod_name]["RAM"] = pod["containers"][0]["usage"]["memory"]
    return metrics

pod_data = get_pod_data(api_client)
metrics = extract_metrics(pod_data)
logging.info(json.dumps(metrics, indent=2))



while True:
    # get metrics from cluster
    pod_data = get_pod_data(api_client)
    metrics = extract_metrics(pod_data)

    # broadcast from socket
    broadcast_socket.send_multipart([b"METRICS", pickle.dumps(metrics)])
    logging.info(json.dumps(metrics, indent=2))

    # sleep 30 seconds
    time.sleep(30)
