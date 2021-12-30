import pickle
import pprint
import queue
import sys
import threading
import zmq

import logging.config

from driver import LoRaHatDriver
from loraconfig import lora_hat_config, logging_config

logging.config.dictConfig(logging_config)


socket_name = "tcp://127.0.0.1:5556"

q = queue.Queue()


def write_to_zeromq(socket_name):
    logging.info(f"binding to {socket_name} for zeroMQ IPC")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(socket_name)
    logging.info("connected to zeroMQ IPC socket")

    while True:
        message = q.get()
        topic_len = message[0]
        topic = message[1 : 1 + topic_len].decode("utf-8")
        data = pickle.loads(message[1 + topic_len :])
        print(topic, data)


threading.Thread(target=write_to_zeromq, daemon=True).start()

with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(f"LoRa hat config: {pprint.pformat(lora_hat.config)}")
    lora_hat.receive(q)
