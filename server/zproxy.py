import zmq
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def main():

    context = zmq.Context()

    # Socket facing producers
    upstream = context.socket(zmq.XSUB)
    upstream.bind("tcp://*:5559")

    # Socket facing consumers
    downstream = context.socket(zmq.XPUB)
    downstream.bind("tcp://*:5560")

    try:
        zmq.proxy(upstream, downstream)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error("Unexpected error: {}".format(str(e)))
    finally:
        upstream.close()
        downstream.close()
        context.term()


if __name__ == "__main__":
    main()
