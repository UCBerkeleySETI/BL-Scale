# client

import zmq
import time
import sys

context = zmq.Context()

socket = context.socket(zmq.PULL)
#socket = context.socket(zmq.REQ)    # uncomment for Req/Rep

socket.connect("tcp://127.0.0.1:5555")


while True:
  #socket.send('')     # uncomment for Req/Rep
  message = socket.recv()
  print ((message))
#   Pipeline does some task

  time.sleep(5)