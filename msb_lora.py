import pickle
import pprint
import queue
import sys
import threading
import time
import zmq

import logging.config

from driver import LoRaHatDriver
from loraconfig import lora_hat_config, logging_config

logging.config.dictConfig(logging_config)

q = queue.Queue()

socket_name = "tcp://127.0.0.1:5556"


def read_from_zeromq(socket_name):
    logging.debug(f"trying to bind zmq to {socket_name}")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    try:
        socket.connect(socket_name)
    except Exception as e:
        logging.critical(f"failed to bind to zeromq socket: {e}")
        sys.exit(-1)

    # subscribe to all available data
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    logging.debug("successfully bound to zeroMQ receiver socket as subscriber")

    while True:
        topic_bin, data_bin = socket.recv_multipart()
        # make sure binary data is still deserializable
        _ = topic_bin.decode("utf-8")
        _ = pickle.loads(data_bin)

        # q.put((topic_bin, data_bin))
        q.put("Got zeroMQ message with topic: ".encode("utf-8") + topic_bin)


threading.Thread(target=read_from_zeromq, daemon=True, args=[socket_name]).start()

with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(f"LoRa hat config: {pprint.pformat(lora_hat.config)}")
    while True:
        # topic_bin, data_bin = q.get()
        #
        # topic_len = len(topic_bin)
        # assert topic_len < 256
        #
        # lora_hat.send(bytes([topic_len]) + topic_bin + data_bin)
        message = q.get()
        lora_hat.send(message)
        time.sleep(0.1)  # limit the number of messages send, otherwise receiver chokes
        # discard messages that are more frequent, maybe use a Timer Thread that sends every x seconds?
        # or does zeromq support this? do we need to read all from zeroMQ or is the last message enough?
