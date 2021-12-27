import socket
import loraconfig
from driver import LoRaHatDriver
import time

config = loraconfig.default.copy()
hostname = socket.gethostname()
with LoRaHatDriver(config) as lora_hat:
    while True:
        lora_hat.send(
            f"{hostname} local time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        time.sleep(2)
