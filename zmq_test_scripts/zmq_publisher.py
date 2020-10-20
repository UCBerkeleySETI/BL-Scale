import zmq
from time import sleep
context = zmq.Context()

socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5000")

messages = [100,200,300,400,500, 600, 700, 800]
curMsg = 0

while True:
    sleep(1)
    print("Sending message...")
    socket.send_pyobj({curMsg:messages[curMsg]})
    if curMsg ==7:
        curMsg = 0
    else:
        curMsg= curMsg + 1
