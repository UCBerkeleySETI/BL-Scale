import zmq


def main():

    context = zmq.Context()

    # Socket facing producers
    upstream = context.socket(zmq.XSUB)
    upstream.bind("tcp://*:5559")

    # Socket facing consumers
    downstream = context.socket(zmq.XPUB)
    downstream.bind("tcp://*:5560")

    zmq.proxy(upstream, downstream)

    # We never get here…
    upstream.close()
    downstream.close()
    context.term()

if __name__ == "__main__":
    main()
