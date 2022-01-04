import zmq
import sys
import logging
from logging.handlers import RotatingFileHandler

from message import TimeOrientPosMessage

plain_formatter = logging.Formatter("%(message)s")

persist_handler = RotatingFileHandler("persist_lora.txt", maxBytes=500, backupCount=5, encoding="utf-8")
persist_handler.setLevel("DEBUG")
persist_handler.setFormatter(plain_formatter)

persist_logger = logging.getLogger(__name__)
persist_logger.setLevel("DEBUG")
persist_logger.addHandler(persist_handler)


socket_name = "tcp://127.0.0.1:5556"
context = zmq.Context()
socket = context.socket(zmq.SUB)
try:
    with socket.connect(socket_name) as connected_socket:
        # subscribe to "LORA" data
        socket.setsockopt(zmq.SUBSCRIBE, "LORA".encode("utf-8"))
        while True:
            topic_bin, data_bin = socket.recv_multipart()
            assert topic_bin == "LORA".encode("utf-8")
            message = TimeOrientPosMessage.from_bytes(data_bin)
            persist_logger.info(repr(message))

except Exception as e:
    logging.critical(f"failed to bind to zeromq socket: {e}")
    sys.exit(-1)





