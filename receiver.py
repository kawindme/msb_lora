import logging
import pprint
import queue
import threading
import sys

from loraconfig import lora_hat_config as config
from loraconfig import logging_basic_config
from driver import LoRaHatDriver

logging.basicConfig(**logging_basic_config)

q = queue.SimpleQueue()


def print_received_data():
    while True:
        print(q.get())


threading.Thread(target=print_received_data, daemon=True).start()

with LoRaHatDriver(config) as lora_hat:
    logging.debug(pprint.pformat(lora_hat.config))
    print("Press \033[1;32mCtrl+C\033[0m to exit")
    lora_hat.receive(q)
