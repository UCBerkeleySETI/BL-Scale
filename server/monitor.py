import zmq
import time
import os
import time
import logging
import sys
import pickle

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.info("Running")

context = zmq.Context()

broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")
