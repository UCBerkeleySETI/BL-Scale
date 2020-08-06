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

    ret_specs = v1.list_pod_for_all_namespaces(watch=False)
    return data, ret_specs

def extract_metrics(pod_data, pod_specs):
    pods = pod_data["items"]
    metrics = defaultdict(dict)
    for pod in pods:
        pod_name = pod["metadata"]["name"]
        if pod["containers"]:
            containers = pod["containers"]
            metrics[pod_name]["CPU"] = containers[0]["usage"]["cpu"]
            metrics[pod_name]["RAM"] = containers[0]["usage"]["memory"]
    for i in pod_specs.items:
        if i.metadata.name in metrics:
            requested = i.spec.containers[0].resources.requests
            metrics[i.metadata.name]["CPU_REQUESTED"] = requested["cpu"]
            if "memory" in requested:
                metrics[i.metadata.name]["RAM_REQUESTED"] = requested["memory"]
    metrics = {pod_name: clean_metrics(pod_metrics) for pod_name, pod_metrics in metrics.items()} # convert metrics to standard units (CPU for cpu, KiB for memory)
    return metrics

def clean_metrics(metrics):
    for name in metrics.keys():
        if name.startswith("CPU"):
            if metrics[name].endswith("m"):
                metrics[name] = int(metrics[name][:-1]) / 1000.0
            elif metrics[name].endswith("n"):
                metrics[name] = int(metrics[name][:-1]) / 1000000000.0
            else:
                metrics[name] = int(metrics[name])
        elif name.startswith("RAM"):
            if metrics[name].endswith("G"):
                metrics[name] = int(metrics[name][:-1]) * 1000000000 / 1024.0
            elif metrics[name].endswith("Gi"):
                metrics[name] = int(metrics[name][:-2]) * 1024*1024
            elif metrics[name].endswith("M"):
                metrics[name] = int(metrics[name][:-1]) * 1000000 / 1024.0
            elif metrics[name].endswith("Mi"):
                metrics[name] = int(metrics[name][:-2]) * 1024
            elif metrics[name].endswith("K"):
                metrics[name] = int(metrics[name][:-1]) * 1000 / 1024.0
    return metrics

pod_data, pod_specs = get_pod_data(api_client)
metrics = extract_metrics(pod_data, pod_specs)
logging.info(json.dumps(metrics, indent=2))



while True:
    # get metrics from cluster
    pod_data, pod_specs = get_pod_data(api_client)
    metrics = extract_metrics(pod_data, pod_specs)

    # broadcast from socket
    broadcast_socket.send_multipart([b"METRICS", pickle.dumps(metrics)])
    logging.info(json.dumps(metrics, indent=2))

    # sleep 30 seconds
    time.sleep(30)
