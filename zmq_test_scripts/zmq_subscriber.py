import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://35.192.178.168:5000")
socket.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    print("Trying to get msg...")
    message = socket.recv_pyobj()
    print(message)