import socket
import loraconfig
from driver import LoRaHatDriver
import time

config = loraconfig.default.copy()

lora_hat = LoRaHatDriver(config)

lora_hat.apply_config()
hostname = socket.gethostname()
while True:
    lora_hat.send(
        f"{hostname} local time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    )
    time.sleep(2)
