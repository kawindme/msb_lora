from driver import serialize_config
from util import command_to_dict
from loraconfig import config


def test_config_serialize():
    conf = config.copy()
    command = serialize_config(conf)
    recovered_conf = command_to_dict(command)
    assert recovered_conf.pop("command") == "Configure temporary registers"
    assert recovered_conf.pop("start_register") == 0
    assert recovered_conf.pop("data_length") == 9

    assert recovered_conf == conf
