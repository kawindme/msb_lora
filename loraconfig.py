from driver import BaudRate, ParityBit, AirSpeed

lora_hat_default = {
    "module_address": 0,
    "net_id": 0,
    "baud_rate": BaudRate.BR_9600,
    "parity_bit": ParityBit.PB_8N1,
    "air_speed": AirSpeed.AS_2_4K,
    "packet_len": 240,
    "enable_ambient_noise": False,
    "transmit_power": "22dBm",
    "channel": 18,  # 18 default for SX1262, 23 default for SX1268
    "enable_RSSI_byte": False,
    "enable_point_to_point_mode": False,
    "enable_relay_function": False,
    "enable_LBT": False,
    "WOR_mode": 0,
    "WOR_period": 500,
    "key": 0,
}

lora_hat_config = lora_hat_default.copy()
lora_hat_config["enable_point_to_point_mode"] = True


try:
    import localconfig

    lora_hat_config.update(localconfig.lora_hat_config)
except ImportError:
    pass
