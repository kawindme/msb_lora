import socket
import time
from loraconfig import lora_hat_config as config
from loraconfig import logging_config
from driver import LoRaHatDriver
import logging
import logging.config
import pprint
import sys

# logging.basicConfig(**logging_basic_config)
logging.config.dictConfig(logging_config)


hostname = socket.gethostname()
with LoRaHatDriver(config) as lora_hat:
    logging.debug(pprint.pformat(lora_hat.config))
    print("Press \033[1;32mCtrl+C\033[0m to exit")
    while True:
        lora_hat.send(
            f"{hostname} local time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        time.sleep(2)
