import zmq
import json
from collections import defaultdict


class Scheduler:
    def __init__(self, context, stage="DEV"):
        self.workers = dict()
        self.idle_workers = set()
        self.context = context
        self.requests = list()
        self.stage = stage

    def connect_worker(self, worker):
        self.workers[worker.id] = worker
        self.idle_workers.add(worker)

    def add_worker(self):
        pass

    def schedule_request(self, serialized):
        if self.idle_workers:
            worker = self.idle_workers.pop()
            worker.schedule(serialized)
            return worker
        else:
            self.requests.append(serialized)

    def update_worker(self, status):
        if status["pod_id"] not in self.workers:
            if ((self.stage == "DEV" and "dev" in status["pod_id"])
               or (self.stage == "PROD" and "dev" not in status["pod_id"])):
                worker = Worker(status["pod_id"], status["pod_ip"], self.context)
                self.workers[status["pod_id"]] = worker
        else:
            worker = self.workers[status["pod_id"]]
        if worker.update(status):
            self.idle_workers.add(worker)


class Worker:
    def __init__(self, id, ip, context):
        self.id = id
        self.ip = ip
        self.context = context
        self.idle = True
        self.last_status = None

    def schedule(self, serialized):
        if self.idle:
            request_send_socket = self.context.socket(zmq.PUSH)
            request_send_socket.connect(f"tcp://{self.ip}:5555")
            request_send_socket.send(serialized)
            self.idle = False
            return True
        else:
            return False

    def update(self, status):
        self.last_status = status
        if status["IDLE"]:
            self.idle = True
        return self.idle

    def __str__(self):
        return f"{self.id} at {self.ip}:5555 \t STATUS: {'IDLE' if self.idle else 'WORKING'}"


def get_pod_data(api_client, v1):
    ret_metrics = api_client.call_api(
        '/apis/metrics.k8s.io/v1beta1/namespaces/' + 'default' + '/pods', 'GET',
        auth_settings=['BearerToken'], response_type='json', _preload_content=False)
    response = ret_metrics[0].data.decode('utf-8')
    data = json.loads(response)

    ret_specs = v1.list_pod_for_all_namespaces(watch=False)
    return data, ret_specs

def create_pod(api_client):
    return api_client.call_api(
        '/api/v1/namespaces/' + 'default' + '/pods', 'POST',
        auth_settings=['BearerToken'], body='../yaml/static-algo-prod.yaml')
    )

def delete_pod(api_client, pod_name):
    return api_client.call_api(
        '/api/v1/namespaces/' + 'default' + '/pods/' + pod_name, 'DELETE',
        auth_settings=['BearerToken'], response_type='json')
    )

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
    # convert metrics to standard units (CPU for cpu, KiB for memory)
    metrics = {pod_name: clean_metrics(pod_metrics) for pod_name, pod_metrics in metrics.items()}
    return metrics


def clean_metrics(metrics):
    for name in metrics.keys():
        if name.startswith("CPU"):
            if metrics[name].endswith("m"):
                metrics[name] = int(metrics[name][:-1]) / 1000.0
            elif metrics[name].endswith("u"):
                metrics[name] = int(metrics[name][:-1]) / 1000000.0
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
            elif metrics[name].endswith("Ki"):
                metrics[name] = int(metrics[name][:-2])
    return metrics
