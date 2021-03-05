# Network Components

## Webapp

### Networking

### Job performed

## Monitor

### Networking

Listens to broadcasted status updates via proxy at tcp://PROXY_ADDRESS:5560

Pings Kubernetes master node for pod status updates at regular intervals (CPU, RAM usage, etc.), broadcasts via proxy at tcp://PROXY_ADDRESS:5560 on topic "METRICS"

### Job performed

Monitors cluster health and reports to frontend.

## Scheduler

### Networking
Receives connection requests from workers at tcp://*:5510

Receives job requests from outside/webapp at tcp://*:5555

Listens to broadcasted status updates via proxy at tcp://PROXY_ADDRESS:5560

### Job performed

Keeps track of workers and available workers, schedules each job to a worker and monitors progress.


## Worker

### Networking

Receives job requests from scheduler/outside at tcp://*:5555

Broadcasts status updates via proxy at tcp://PROXY_ADDRESS:5560 on topic b"STATUS"

Broadcasts user messages via proxy at tcp://PROXY_ADDRESS:5560 on topic b"MESSAGE"

### Job performed

Runs the job requests by calling the specified algorithm on the data file.

The algorithm is run inside its own virtual environment through `virtual_env_dir/python3 algorithm.py data_file`

Files are first output to a buffer directory, then uploaded to the storage buckets through a FUSE mount.

## Proxy

### Networking

Listens for messages at tcp://PROXY_ADDRESS:5559, and broadcasts then through tcp://PROXY_ADDRESS:5560

### Job performed

The proxy exists because we want every component inside the cluster to be able to broadcast messages to every other component. With normal PUB/SUB sockets, subscribers listen to a single broadcaster, and won't be able to listen to all the machines in the cluster with just one socket. With the proxy, we can have every component sending messages they want to broadcast to the proxy, and have all components listening to the proxy. This allows us to establish a many-to-many connection between all the components.
