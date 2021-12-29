import socket
import time
from loraconfig import lora_hat_config as config
from driver import LoRaHatDriver


hostname = socket.gethostname()
with LoRaHatDriver(config) as lora_hat:
    while True:
        lora_hat.send(
            f"{hostname} local time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        time.sleep(2)
