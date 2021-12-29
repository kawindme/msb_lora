import queue
import threading

from loraconfig import lora_hat_config as config
from driver import LoRaHatDriver

q = queue.SimpleQueue()

def print_received_data():
    while True:
        print(q.get())


threading.Thread(target=print_received_data, daemon=True).start()

with LoRaHatDriver(config) as lora_hat:
    lora_hat.receive(q)
