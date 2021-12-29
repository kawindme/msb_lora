from driver import serialize_config
from util import command_to_dict
from loraconfig import lora_hat_config


def test_config_serialize():
    conf = lora_hat_config.copy()
    command = serialize_config(conf)
    recovered_conf = command_to_dict(command)
    assert recovered_conf.pop("command") == "Configure temporary registers"
    assert recovered_conf.pop("start_register") == 0
    assert recovered_conf.pop("data_length") == 9

    assert recovered_conf == conf

def test_config_example_relay():
    relay_config_bytes= b'\xC2\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00'
    conf_dict = command_to_dict(relay_config_bytes)
    recovered_config_bytes = serialize_config(conf_dict)

    assert relay_config_bytes == recovered_config_bytes


def test_config_example_transparent_scx126x():
    sx126x_config_bytes = bytes([0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x17, 0x00, 0x00, 0x00])
    conf_dict = command_to_dict(sx126x_config_bytes)
    recovered_config_bytes = serialize_config(conf_dict)

    assert sx126x_config_bytes == recovered_config_bytes