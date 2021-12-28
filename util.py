from collections.abc import Sequence


def translate_0(byte_val: int) -> str:
    """Command byte"""
    if byte_val == 0xC2:
        return "Configure temporary registers"
    elif byte_val == 0xC1:
        return "Answer / Read registers"
    elif byte_val == 0xC0:
        return "Configure registers"
    else:
        raise ValueError(f"Unknown register value {byte_val}")


def translate_1(byte_val: int) -> int:
    """Start register"""
    assert 0 <= byte_val < 8
    return byte_val


def translate_2(byte_val: int) -> int:
    """Length of data"""
    assert 0 <= byte_val <= 9
    return byte_val


def translate_3_4(byte_val_3: int, byte_val_4: int) -> int:
    """Module address"""
    assert 0 <= byte_val_3 < 256
    assert 0 <= byte_val_4 < 256
    # module address has 16 bit = 2 byte
    # byte_val_3 are high bits of module address
    # byte_val_4 are low bits of module address
    # shifting byte_val_3 8 bits to the left makes them the high bits of a 16 bit number
    # these high bits can then be logically or'ed with the lower bits
    return byte_val_3 << 8 | byte_val_4


def translate_5(byte_val: int) -> int:
    """Net ID"""
    assert 0 <= byte_val < 256
    return byte_val


def translate_6(byte_val: int) -> dict:
    """baud rate(7-5), parity bit(4-3), wireless air speed / bps (2-0)"""
    assert 0 <= byte_val < 256

    baud_rate_mask = 0b11100000
    baud_rate_shift = 5
    parity_bit_mask = 0b00011000
    parity_bit_shift = 3
    air_speed_mask = 0b00000111
    air_speed_shift = 0

    baud_rate_val = (byte_val & baud_rate_mask) >> baud_rate_shift
    parity_bit_val = (byte_val & parity_bit_mask) >> parity_bit_shift
    air_speed_val = (byte_val & air_speed_mask) >> air_speed_shift

    baud_rate_dict = {
        0b000: 1200,
        0b001: 2400,
        0b010: 4800,
        0b011: 9600,
        0b100: 19200,
        0b101: 38400,
        0b110: 57600,
        0b111: 115200,
    }
    baud_rate = baud_rate_dict[baud_rate_val]

    parity_bit_dict = {0b00: "8N1", 0b01: "8O1", 0b10: "8E1", 0b11: "8N1"}
    parity_bit = parity_bit_dict[parity_bit_val]

    air_speed_dict = {
        0b000: "0.3K",
        0b001: "1.2K",
        0b010: "2.4K",
        0b011: "4.8K",
        0b100: "9.6K",
        0b101: "19.2K",
        0b110: "38.4K",
        0b111: "62.5K",
    }
    air_speed = air_speed_dict[air_speed_val]

    return {"baud_rate": baud_rate, "parity_bit": parity_bit, "air_speed": air_speed}


def translate_7(byte_val: int) -> dict:
    """
    packet_len(7-6), enable_ambient_noise(5), transmit_power(1-0)

    (reserved / unused: (4-2))
    """
    packet_len_mask = 0b11000000
    packet_len_shift = 6
    enable_ambient_noise_mask = 0b00100000
    enable_ambient_noise_shift = 5
    reserved_mask = 0b00011100
    reserved_shift = 2
    transmit_power_mask = 0b00000011
    transmit_power_shift = 0

    packet_len_val = (byte_val & packet_len_mask) >> packet_len_shift
    enable_ambient_noise_val = (
        byte_val & enable_ambient_noise_mask
    ) >> enable_ambient_noise_shift
    reserved_val = (byte_val & reserved_mask) >> reserved_shift
    transmit_power_val = (byte_val & transmit_power_mask) >> transmit_power_shift

    assert reserved_val == 0
    del reserved_val

    packet_len_dict = {0b00: 240, 0b01: 128, 0b10: 64, 0b11: 32}
    packet_len = packet_len_dict[packet_len_val]

    enable_ambient_noise = bool(enable_ambient_noise_val)

    transmit_power_dict = {0b00: "22dbm", 0b01: "17dbm", 0b10: "12dbm", 0b11: "10dbm"}
    transmit_power = transmit_power_dict[transmit_power_val]

    return {
        "packet_len": packet_len,
        "enable_ambient_noise": enable_ambient_noise,
        "transmit_power": transmit_power,
    }


def translate_8(byte_val: int) -> int:
    """
    Channel control (CH) 0-83. 84 channels in total

    850.125 + CH *1MHz. Default 868.125MHz(SX1262),
    410.125 + CH *1MHz. Default 433.125MHz(SX1268)
    """
    assert 0 <= byte_val <= 83
    return byte_val


def translate_9(byte_val: int) -> dict:
    """
    enable_RSSI_byte(7), enable_transmitting_mode(6), enable_relay_function(5), enable_LBT(4), WOR_mode(3), WOR_period (2-0)
    """
    enable_RSSI_byte_mask = 0b10000000
    enable_RSSI_byte_shift = 7
    enable_transmitting_mode_mask = 0b01000000
    enable_transmitting_mode_shift = 6
    enable_relay_function_mask = 0b00100000
    enable_relay_function_shift = 5
    enable_LBT_mask = 0b00010000
    enable_LBT_shift = 4
    WOR_mode_mask = 0b00001000
    WOR_mode_shift = 3
    WOR_period_mask = 0b00000111
    WOR_period_shift = 0

    enable_RSSI_byte_value = (
        byte_val & enable_RSSI_byte_mask
    ) >> enable_RSSI_byte_shift
    enable_transmitting_mode_value = (
        byte_val & enable_transmitting_mode_mask
    ) >> enable_transmitting_mode_shift
    enable_relay_function_value = (
        byte_val & enable_relay_function_mask
    ) >> enable_relay_function_shift
    enable_LBT_value = (byte_val & enable_LBT_mask) >> enable_LBT_shift
    WOR_mode_value = (byte_val & WOR_mode_mask) >> WOR_mode_shift
    WOR_period_value = (byte_val & WOR_period_mask) >> WOR_period_shift

    enable_RSSI_byte = bool(enable_RSSI_byte_value)
    enable_transmitting_mode = bool(enable_transmitting_mode_value)
    enable_relay_function = bool(enable_relay_function_value)
    enable_LBT = bool(enable_LBT_value)
    WOR_mode = WOR_mode_value

    WOR_period_dict = {
        0b000: 500,
        0b001: 1000,
        0b010: 1500,
        0b011: 2000,
        0b100: 2500,
        0b101: 3000,
        0b110: 3500,
        0b111: 4000,
    }

    WOR_period = WOR_period_dict[WOR_period_value]

    return {
        "enable_RSSI_byte": enable_RSSI_byte,
        "enable_transmitting_mode": enable_transmitting_mode,
        "enable_relay_function": enable_relay_function,
        "enable_LBT": enable_LBT,
        "WOR_mode": WOR_mode,
        "WOR_period": WOR_period,
    }


def translate_10_11(byte_val_10: int, byte_val_11: int) -> int:
    """Key"""
    assert 0 <= byte_val_10 < 256
    assert 0 <= byte_val_11 < 256
    # key has 16 bit = 2 byte
    # byte_val_10 are high bits of module address
    # byte_val_11 are low bits of module address
    # shifting byte_val_10 8 bits to the left makes them the high bits of a 16 bit number
    # these high bits can then be logically or'ed with the lower bits
    return byte_val_10 << 8 | byte_val_11


def command_to_dict(command_bytes: Sequence[int]) -> dict:
    assert len(command_bytes) == 12

    command_dict = {}
    command_dict["command"] = translate_0(command_bytes[0])
    command_dict["start_register"] = translate_1(command_bytes[1])
    command_dict["data_length"] = translate_2(command_bytes[2])
    command_dict["module_address"] = translate_3_4(command_bytes[3], command_bytes[4])
    command_dict["net_id"] = translate_5(command_bytes[5])
    command_dict.update(translate_6(command_bytes[6]))
    command_dict.update(translate_7(command_bytes[7]))
    command_dict["channel"] = translate_8(command_bytes[8])
    command_dict.update(translate_9(command_bytes[9]))
    command_dict["key"] = translate_10_11(command_bytes[10], command_bytes[11])

    return command_dict


if __name__ == "__main__":

    reg_array = [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x17, 0x00, 0x00, 0x00]

    command_dict = command_to_dict(reg_array)

    pass
# f"{194:b}"
#'11000010'
# f"{194:x}"
#'c2'
# f"{194:#x}"
#'0xc2'
