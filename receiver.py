import loraconfig
from driver import LoRaHatDriver

config = loraconfig.default.copy()

lora_hat = LoRaHatDriver(config)
lora_hat.apply_config()
lora_hat.receive()
