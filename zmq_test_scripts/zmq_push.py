# server

import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.PUSH)

socket.bind("tcp://127.0.0.1:5555")

i = 0
time.sleep(1)   # naive wait for clients to arrive

while True:
  print(i)
  socket.send(str.encode(str(i)))
  i += 1 
  time.sleep(1)

time.sleep(10)   # naive wait for tasks to drain