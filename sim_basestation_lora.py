import itertools
import time

import zmq
import numpy as np

import logging.config

from loraconfig import logging_config_dict
from message import TimeOrientPosMessage, Topic

logging.config.dictConfig(logging_config_dict)


socket_name = "tcp://127.0.0.1:5555"

logging.info(f"binding to {socket_name} for zeroMQ IPC")
context = zmq.Context()
socket = context.socket(zmq.PUB)
with socket.connect(socket_name):
    logging.info("connected to zeroMQ IPC socket")
    sender_iter = itertools.cycle([150, 151, 153])
    while True:
        data = np.random.standard_normal(8).astype(TimeOrientPosMessage.array_dtype)
        sender = next(sender_iter)
        message = TimeOrientPosMessage(data, sender, topic=Topic.ATTITUDE)
        socket.send_multipart(["LORA".encode("utf-8"), message.serialize()])  # topic
        time.sleep(0.3)
