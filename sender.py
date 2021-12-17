#!/usr/bin/python
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
import serial
import time
import sys

M0 = 22
M1 = 27

#https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT

"""

    header  start number REG0 REG1 REG2 REG3 REG4 REG5 REG6 REG7 REG8
    0xC2    0x00  0x09   0x01 0x02 0x03 0x62 0x00 0x12 0x03 0x00 0x00

0xC2 is command header
0x00 is the start register you want to set
0x09 is the 9 registers you want to set

REG0...REG8,total 9 registers parameter,REG0 is ADDH register,REG8 is CRYPT_L register

REG5 is the channel register,SX1268 is from 410MHz to 483MHz,SX1262 is from 850MHz to 930MHz

the calculation is like that :
433MHz = 410MHz + REG5(0x17,default value)
470MHz = 410MHz + REG5(0x3C)
868MHz = 850MHz + REG5(0x12,default value)
915MHz = 850MHz + REG5(0x41)

433MHz
CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x17\x03\x00\x00']
RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x17\x03\x00\x00']

470MHz
CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x3C\x03\x00\x00']
RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x3C\x03\x00\x00']

868MHz
CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']
RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']

915MHz
CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x41\x03\x00\x00']
RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x41\x03\x00\x00']

"""

"""
REG0:

"""

get_reg_03H(baud_rate=9600, parity_bit="8N1", air_speed="2.4K"):
    """baud rate(7-5), parity bit(4-3), wireless air speed / bps (2-0)"""

    baud_rate_dict =
        {1200: "000",
         2400: "001",
         4800: "010",
         9600: "011",
         19200: "100",
         38400: "101",
         57600: "110",
         115200: "111",
        }
    try:
        baud_rate_str = baud_rate_dict[baud_rate]
    except KeyError:
        raise RuntimeError(f"Unknown baud rate {baud_rate}. Possible values are {baud_rate_dict.keys()}.")

    parity_bit_dict =
        {"8N1": "00",
         "8O1": "01",
         "8E1": "10",
        }
    try:
        parity_bit_str = parity_bit_dict[parity_bit]
    except KeyError:
        raise RuntimeError(f"Unknown parity bit {parity_bit}. Possible values are {parity_bit_dict.keys()}.")

    air_speed_dict =
        {"0.3K": "000",
         "1.2K": "001",
         "2.4K": "010",
         "4.8K": "011",
         "9.6K": "100",
         "19.2K": "101",
         "38.4K": "110",
         "62.5K": "111",
        }

    try:
        air_speed_str = air_speed_dict[air_speed]
    except KeyError:
        raise RuntimeError(f"Unknown air speed {air_speed}. Possible values are {air_speed_dict.keys()}.")

    return int(baud_rate_str + parity_bit_str + air_speed_str, 2)

get_reg_04H(packet_len=240, enable_ambient_noise=False, transmit_power="22dBm"):
    packet_len_dict =
        {240: "00",
         128: "01",
         64: "10",
         32: "11",
        }

    try:
        packet_len_str = packet_len_dict[packet_len]
    except KeyError:
        raise RuntimeError(f"Unknown air speed {packet_len}. Possible values are {packet_len_dict.keys()}.")

    if not enable_ambient_noise:
        ambient_noise_str = "0"
    else:
        ambient_noise_str = "1"

    transmit_power_dict =
        {"22dbm": "00",
         "17dbm": "01",
         "12dbm": "10",
         "10dbm": "11",
        }

    try:
        transmit_power_str = transmit_power_dict[transmit_power.lower()]
    except KeyError:
        raise RuntimeError(f"Unknown transmit_power {transmit_power}. Possible values are {transmit_power_dict.keys()}.")

    return int(packet_len_str + ambient_noise_str + transmit_power_str, 2)

get_reg_05H(channel=18): # 18 default for SX1262, 23 default for SX1268
    """
    Channel control (CH) 0-83. 84 channels in total

    850.125 + CH *1MHz. Default 868.125MHz(SX1262),
    410.125 + CH *1MHz. Default 433.125MHz(SX1268)
    """
    if channel >=0 and channel <= 83:
        return channel
    else:
        raise RuntimeError(f"Invalid channel, channel must be between 0-83, but was {channel}."

get_reg_06H(enable_RSSI_byte=False, enable_transmitting_mode=False, enable_relay_function=False, enable_LBT=False, set_WOR_mode=0, WOR_period=500):
    """
    enable_RSSI_byte:
        After enabling, data sent to serial port is added with a RSSI byte after receiving

    enable_transmitting_mode:
        When point to point transmitting, module will recognize the first three byte as Address High + Address Low + Channel. and wireless transmit it

    enable_relay_function:
        If target address is not module itself, module will forward data;To avoid data echo, we recommend you to use this function in point to point mode, that is target address is different with source address

    enable_LBT:
        Module will listen before transmit wireless data. This function can be used to avoid interference, however, it also clause longer latency; The MAX LBT time is 2s, after 2s, data is forced to transmit

    set_WOR_mode:
        This setting only work for Mode 1;
        Receiver waits for 1000ms after receive wirelesss data and forward,and then enter WOR mode again
        User can send data to serial port and forward via wireless network during this interval,
        Every serial byte will refresh this interval time (1000ms);
        You much send the first byte in 1000ms.
        0 -> WOR transmit (default) Module is enabled to receive/transmit, and wakeup code is added to transmitted data.
        1 -> WOR Sender Module is disable to send data. Module is working in WOR listen mode. Consumption is reduced

    WOR_period:
        This setting only work for Mode 1;
        Period is equal to T = (1 + WOR) * 500ms; MAX 4000ms, MIN 500ms
        Longer the Period time of WOR listen, lower the average consumption, however, longer the latency
        The settings of receiver and sender must be same.
    """

    RSSI_byte_str = "0" if not enable_RSSI_byte else "1"
    transmitting_mode_str = "0" if not enable_transmitting_mode else "1"
    relay_function_str = "0" if not enable_relay_function else "1"
    LBT_str = "0" if not enable_LBT else "1"

    WOR_mode_str = "0" if set_WOR_mode == 0 else "1"

    WOR_period_dict =
        {500: "000",
         1000: "001",
         1500: "010",
         2000: "011",
         2500: "100",
         3000: "101",
         3500: "110",
         4000: "111",
        }
    try:
        WOR_period_str = WOR_period_dict[WOR_period]
    except KeyError:
        raise RuntimeError(f"Unknown WOR period {WOR_period}. Possible values are {WOR_period_dict.keys()}.")


    return int(RSSI_byte_str + transmitting_mode_str + relay_function_str + LBT_str + WOR_mode_str + WOR_period_str, 2)


get_reg_07H(key=0):
    """High bytes of Key (default 0)

    Only write enable, the read result always be 0;

    This key is used to encrypting to avoid wireless data intercepted by similar modules;
    This key is work as calculation factor when module is encrypting wireless data.
    """

    key_str = format(key, '016b')
    assert len(key_str) == 16
    return int(key_str[:8], 2)

get_reg_08H(key=0):
    """Low bytes of Key (default 0)

    Only write enable, the read result always be 0;

    This key is used to encrypting to avoid wireless data intercepted by similar modules;
    This key is work as calculation factor when module is encrypting wireless data.
    """

    key_str = format(key, '016b')
    assert len(key_str) == 16
    return int(key_str[8:], 2)





CFG_HEADER = b"\xC2" # use if we want to set registers
RET_HEADER = b"\xC1" # answer after regiersters have been set, use to check if successful
START_REG = b"\x00" # begin with the first register
NUM_REG = b"\x09" # set 9 registers

