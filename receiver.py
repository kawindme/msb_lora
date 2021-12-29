import logging
import pprint
import queue
import threading
import sys

from loraconfig import lora_hat_config as config
from driver import LoRaHatDriver

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

q = queue.SimpleQueue()


def print_received_data():
    while True:
        print(q.get())


threading.Thread(target=print_received_data, daemon=True).start()

with LoRaHatDriver(config) as lora_hat:
    logging.debug(pprint.pformat(lora_hat.config))
    lora_hat.receive(q)
