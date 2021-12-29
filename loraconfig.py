lora_hat_default = {
    "module_address": 0,
    "net_id": 0,
    "baud_rate": 9600,
    "parity_bit": "8N1",
    "air_speed": "2.4K",
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
#lora_hat_config["enable_point_to_point_mode"] = True
#lora_hat_config["enable_relay_function"] = True


try:
    import localconfig

    lora_hat_config.update(localconfig.lora_hat_config)
except ImportError:
    pass
