from kubernetes import client, config
import zmq
import time
import logging
import sys
import pickle
import json
from utils import get_pod_data, extract_metrics, Scheduler, Worker

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.info("Running")

########################################
# ZMQ Sockets Setup
########################################

context = zmq.Context()

connect_recv_socket = context.socket(zmq.PULL)
connect_recv_socket.bind("tcp://*:5510")

request_recv_socket = context.socket(zmq.PULL)
request_recv_socket.bind("tcp://*:5555")

broadcast_pub_socket = context.socket(zmq.PUB)
broadcast_pub_socket.connect("tcp://10.0.3.141:5559")

broadcast_sub_socket = context.socket(zmq.SUB)
broadcast_sub_socket.connect("tcp://10.0.3.141:5560")
broadcast_sub_socket.setsockopt(zmq.SUBSCRIBE, b'STATUS')

error_sub_socket = context.socket(zmq.SUB)
error_sub_socket.connect("tcp://10.0.3.141:5560")
error_sub_socket.setsockopt(zmq.SUBSCRIBE, b'ERROR')

# set up poller, for polling messages from request_recv_socket
poller = zmq.Poller()
poller.register(connect_recv_socket, zmq.POLLIN)
poller.register(request_recv_socket, zmq.POLLIN)
poller.register(broadcast_sub_socket, zmq.POLLIN)
poller.register(error_sub_socket, zmq.POLLIN)

########################################
# set up kubernetes client
########################################

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

########################################
# set up scheduler abstraction
########################################
scheduler = Scheduler(context)

########################################
# Run event loop
########################################

last_info_time = int(time.time())

while True:
    sockets = dict(poller.poll(2))

    if connect_recv_socket in sockets and sockets[connect_recv_socket] == zmq.POLLIN:
        connect = connect_recv_socket.recv_pyobj()
        if connect["pod_id"] not in scheduler.workers:
            new_worker = Worker(connect["pod_id"], connect["pod_ip"], context)
            scheduler.connect_worker(new_worker)
            logging.info(f"Connected worker {connect['pod_id']} at {connect['pod_ip']}")

    if request_recv_socket in sockets and sockets[request_recv_socket] == zmq.POLLIN:
        serialized = request_recv_socket.recv()
        scheduler.schedule_request(serialized)

    if broadcast_sub_socket in sockets and sockets[broadcast_sub_socket] == zmq.POLLIN:
        serialized_status = broadcast_sub_socket.recv_multipart()[1]
        status = pickle.loads(serialized_status)
        logging.info(f"Received status update: {status}")
        scheduler.update_worker(status)

        if scheduler.requests:
            scheduler.schedule_request(scheduler.requests.pop(0))

    if error_sub_socket in sockets and sockets[error_sub_socket] == zmq.POLLIN:
        serialized_error_status = error_sub_socket.recv_multipart()[1]
        error_status = pickle.loads(serialized_error_status)
        pod_id = error_status['pod_id']
        logging.error(f"Received failure on pod with id: {pod_id}")
        request = scheduler.workers[pod_id].request
        scheduler.schedule_request(request)

    if int(time.time()) % 60 == 0 and int(time.time()) != last_info_time:
        logging.info("scheduler running normally")
        logging.info(f"Idle workers: {scheduler.idle_workers}")
        last_info_time = int(time.time())
