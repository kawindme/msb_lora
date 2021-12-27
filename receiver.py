import queue
import threading

import loraconfig
from driver import LoRaHatDriver

config = loraconfig.default.copy()

q = queue.SimpleQueue()


def print_received_data():
    while True:
        print(q.get())


threading.Thread(target=print_received_data, daemon=True).start()

with LoRaHatDriver(config) as lora_hat:
    lora_hat.receive(q)
