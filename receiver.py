import loraconfig
from driver import LoRaHatDriver

config = loraconfig.default.copy()

with LoRaHatDriver(config) as lora_hat:
    lora_hat.receive()  # TODO write to file?
