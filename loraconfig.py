import logging
import os
import sys

from driver import (
    BaudRate,
    ParityBit,
    AirSpeed,
    PacketLen,
    TransmitPower,
    WORMode,
    WORPeriod,
)

logging_basic_config = {
    # "filename": "",
    "stream": sys.stdout,
    "level": logging.DEBUG,
    "format": "%(levelname)s: %(asctime)s %(message)s",
    "datefmt": "%Y%m%dT%H%M%S%z",
}

lora_hat_default = {
    "module_address": 0,
    "net_id": 0,
    "baud_rate": BaudRate.BR_9600,
    "parity_bit": ParityBit.PB_8N1,
    "air_speed": AirSpeed.AS_2_4K,
    "packet_len": PacketLen.PL_240B,
    "enable_ambient_noise": False,
    "transmit_power": TransmitPower.TP_22dBm,
    "channel": 18,  # 18 default for SX1262, 23 default for SX1268
    "enable_RSSI_byte": False,
    "enable_point_to_point_mode": False,
    "enable_relay_function": False,
    "enable_LBT": False,
    "WOR_mode": WORMode.WOR_transmit,
    "WOR_period": WORPeriod.WP_500ms,
    "key": 0,
}

lora_hat_config = lora_hat_default.copy()
lora_hat_config["enable_point_to_point_mode"] = True

# (Partly) overwrite with localconfig
try:
    import localconfig

    lora_hat_config.update(localconfig.lora_hat_config)
except ImportError:
    pass


try:
    lora_hat_config["key"] = int(os.environ["MSB_LORA_HAT_KEY"])
except KeyError:  # Environment variable not set
    pass

if lora_hat_config["key"] == 0:
    logging.warning("No secret key set.")
