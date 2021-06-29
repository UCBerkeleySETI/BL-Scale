import zmq

context = zmq.Context()
request_send_socket = context.socket(zmq.PUSH)
request_send_socket.connect("tcp://34.122.126.21:5555")

request = dict()

request["alg_package"] = ""
request["alg_name"] = ""
request["input_file_url"] = ""

request_send_socket.send_pyobj(request)
