default = {
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
    "enable_transmitting_mode": False,
    "enable_relay_function": False,
    "enable_LBT": False,
    "WOR_mode": 0,
    "WOR_period": 500,
    "key": 0,
}

config = default.copy()
config["enable_transmitting_mode"] = True


try:
    import localconfig

    config.update(localconfig.config)
except ImportError:
    pass
