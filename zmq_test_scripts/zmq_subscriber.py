import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://<insert ip here>:<port number here>")
socket.setsocketopt(zmq.SUBSCRIBE, '')

while True:
    message = socket.recv_pyobj()
    print(message)