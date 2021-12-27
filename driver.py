#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import RPi.GPIO as GPIO
import serial
import time
import sys

try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

# https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT

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


class LoRaHatDriver:

    M0 = 22
    M1 = 27

    CFG_HEADER = b"\xC2"  # Header to use if we want to set registers.
    RET_HEADER = b"\xC1"  # Header of the answer after registers have been set. Use it to check if set was successful.
    START_REG = b"\x00"  # begin with the first register
    NUM_REG = b"\x09"  # set 9 registers

    def __init__(self, config):
        self.module_address = config["module_address"]
        self.net_id = config["net_id"]
        self.baud_rate = config["baud_rate"]
        self.parity_bit = config["parity_bit"]
        self.air_speed = config["air_speed"]
        self.packet_len = config["packet_len"]
        self.enable_ambient_noise = config["enable_ambient_noise"]
        self.transmit_power = config["transmit_power"]
        self.channel = config["channel"]
        self.enable_RSSI_byte = config["enable_RSSI_byte"]
        self.enable_transmitting_mode = config["enable_transmitting_mode"]
        self.enable_relay_function = config["enable_relay_function"]
        self.enable_LBT = config["enable_LBT"]
        self.WOR_mode = config["WOR_mode"]
        self.WOR_period = config["WOR_period"]
        self.key = config["key"]

        GPIO.setmode(GPIO.BCM)  # https://raspberrypi.stackexchange.com/a/12967
        GPIO.setwarnings(False)  # suppress channel already in use warning
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)

        # create serial object but do not open file yet
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyS0"
        self.ser.baudrate = self.baud_rate

    def __enter__(self):
        self.apply_config()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ser.close()
        GPIO.cleanup()
        print("Successfully shut down.")

    def get_reg_00H(self, module_address=0):
        """High bits of module address. Note that when module address is 0xFFFF (=65535).

        It works as broadcasting and listening address and LoRa module doesn't filter address anymore.
        """

        assert 0 <= module_address < 2 ** 16
        address_str = format(module_address, "016b")
        assert len(address_str) == 16
        return int(address_str[:8], 2)

    def get_reg_01H(self, module_address=0):
        """Low bits of module address. Note that when module address is 0xFFFF (=65535).

        It works as broadcasting and listening address and LoRa module doesn't filter address anymore
        """

        assert 0 <= module_address < 2 ** 16
        address_str = format(module_address, "016b")
        assert len(address_str) == 16
        return int(address_str[8:], 2)

    def get_reg_02H(self, net_id=0):
        """Network ID, it is used to distinguish network.

        If you want to communicating between two modules, you need to set their NETID to same ID"""

        if 0 <= net_id <= 256 and type(net_id) == int:
            return net_id
        else:
            raise ValueError(
                f"net_id must be an int between 0 and 256, but was {net_id}."
            )

    def get_reg_03H(self, baud_rate=9600, parity_bit="8N1", air_speed="2.4K"):
        """baud rate(7-5), parity bit(4-3), wireless air speed / bps (2-0)"""

        baud_rate_dict = {
            1200: "000",
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
            raise RuntimeError(
                f"Unknown baud rate {baud_rate}. Possible values are {baud_rate_dict.keys()}."
            )

        parity_bit_dict = {
            "8N1": "00",
            "8O1": "01",
            "8E1": "10",
        }
        try:
            parity_bit_str = parity_bit_dict[parity_bit]
        except KeyError:
            raise RuntimeError(
                f"Unknown parity bit {parity_bit}. Possible values are {parity_bit_dict.keys()}."
            )

        air_speed_dict = {
            "0.3K": "000",
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
            raise RuntimeError(
                f"Unknown air speed {air_speed}. Possible values are {air_speed_dict.keys()}."
            )

        return int(baud_rate_str + parity_bit_str + air_speed_str, 2)

    def get_reg_04H(
        self, packet_len=240, enable_ambient_noise=False, transmit_power="22dBm"
    ):
        packet_len_dict = {
            240: "00",
            128: "01",
            64: "10",
            32: "11",
        }

        try:
            packet_len_str = packet_len_dict[packet_len]
        except KeyError:
            raise RuntimeError(
                f"Unknown air speed {packet_len}. Possible values are {packet_len_dict.keys()}."
            )

        if not enable_ambient_noise:
            ambient_noise_str = "0"
        else:
            ambient_noise_str = "1"

        transmit_power_dict = {
            "22dbm": "00",
            "17dbm": "01",
            "12dbm": "10",
            "10dbm": "11",
        }

        try:
            transmit_power_str = transmit_power_dict[transmit_power.lower()]
        except KeyError:
            raise RuntimeError(
                f"Unknown transmit_power {transmit_power}. Possible values are {transmit_power_dict.keys()}."
            )

        return int(packet_len_str + ambient_noise_str + transmit_power_str, 2)

    def get_reg_05H(self, channel=18):  # 18 default for SX1262, 23 default for SX1268
        """
        Channel control (CH) 0-83. 84 channels in total

        850.125 + CH *1MHz. Default 868.125MHz(SX1262),
        410.125 + CH *1MHz. Default 433.125MHz(SX1268)
        """
        if 0 <= channel <= 83:
            return channel
        else:
            raise RuntimeError(
                f"Invalid channel, channel must be between 0-83, but was {channel}."
            )

    def get_reg_06H(
        self,
        enable_RSSI_byte=False,
        enable_transmitting_mode=False,
        enable_relay_function=False,
        enable_LBT=False,
        WOR_mode=0,
        WOR_period=500,
    ):
        """
        enable_RSSI_byte:
            After enabling, data sent to serial port is added with a RSSI byte after receiving

        enable_transmitting_mode:
            When point to point transmitting, module will recognize the first three byte as
            Address High + Address Low + Channel. and wireless transmit it

        enable_relay_function:
            If target address is not module itself, module will forward data;
            To avoid data echo, we recommend you to use this function in point to point mode,
            that is target address is different with source address

        enable_LBT:
            Module will listen before transmit wireless data. This function can be used to avoid interference,
            however, it also clause longer latency; The MAX LBT time is 2s, after 2s, data is forced to transmit

        WOR_mode:
            This setting only work for Mode 1;
            Receiver waits for 1000ms after receive wireless data and forward,and then enter WOR mode again
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

        WOR_mode_str = "0" if WOR_mode == 0 else "1"

        WOR_period_dict = {
            500: "000",
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
            raise RuntimeError(
                f"Unknown WOR period {WOR_period}. Possible values are {WOR_period_dict.keys()}."
            )

        return int(
            RSSI_byte_str
            + transmitting_mode_str
            + relay_function_str
            + LBT_str
            + WOR_mode_str
            + WOR_period_str,
            2,
        )

    def get_reg_07H(self, key=0):
        """High bytes of Key (default 0)

        Only write enable, the read result always be 0;

        This key is used to encrypting to avoid wireless data intercepted by similar modules;
        This key is work as calculation factor when module is encrypting wireless data.
        """
        assert 0 <= key < 2 ** 16
        key_str = format(key, "016b")
        assert len(key_str) == 16
        return int(key_str[:8], 2)

    def get_reg_08H(self, key=0):
        """Low bytes of Key (default 0)

        Only write enable, the read result always be 0;

        This key is used to encrypting to avoid wireless data intercepted by similar modules;
        This key is work as calculation factor when module is encrypting wireless data.
        """
        assert 0 <= key < 2 ** 16
        key_str = format(key, "016b")
        assert len(key_str) == 16
        return int(key_str[8:], 2)

    def apply_config(self):

        cfg_bytes = bytearray(12)
        # set header
        cfg_bytes[0] = self.CFG_HEADER[0]
        cfg_bytes[1] = self.START_REG[0]
        cfg_bytes[2] = self.NUM_REG[0]
        # set registers
        cfg_bytes[3] = self.get_reg_00H(self.module_address)
        cfg_bytes[4] = self.get_reg_01H(self.module_address)
        cfg_bytes[5] = self.get_reg_02H(self.net_id)
        cfg_bytes[6] = self.get_reg_03H(self.baud_rate, self.parity_bit, self.air_speed)
        cfg_bytes[7] = self.get_reg_04H(
            self.packet_len, self.enable_ambient_noise, self.transmit_power
        )
        cfg_bytes[8] = self.get_reg_05H(self.channel)
        cfg_bytes[9] = self.get_reg_06H(
            self.enable_RSSI_byte,
            self.enable_transmitting_mode,
            self.enable_relay_function,
            self.enable_LBT,
            self.WOR_mode,
            self.WOR_period,
        )
        cfg_bytes[10] = self.get_reg_07H(self.key)
        cfg_bytes[11] = self.get_reg_08H(self.key)

        ret_bytes = cfg_bytes.copy()
        ret_bytes[0] = self.RET_HEADER[0]

        cfg_bytes = bytes(cfg_bytes)
        ret_bytes = bytes(ret_bytes)

        # enter configuration mode
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(1)

        self.ser.open()
        self.ser.reset_input_buffer()
        print("Press \033[1;32mCtrl+C\033[0m to exit")

        if self.ser.is_open:
            print("Serial port is open, trying to write configuration.")
            self.ser.write(cfg_bytes)
            wait_counter = 0
            while True:
                if self.ser.in_waiting > 0:  # there is something to read
                    time.sleep(0.1)
                    read_buffer = self.ser.read(self.ser.in_waiting)
                    if read_buffer == ret_bytes:
                        print("Successfully applied configuration.")
                        # enter operation mode
                        GPIO.output(self.M1, GPIO.LOW)
                        time.sleep(0.01)
                        break
                elif wait_counter >= 100:
                    print("Could not apply configuration. Aborting.")
                    break
                else:
                    time.sleep(0.1)
                    wait_counter += 1

    def send(self, message):
        # message = message + "\r\n"
        message = message + "\n"
        self.ser.write(message.encode("ascii"))

    def receive(self, q):
        while True:
            if self.ser.in_waiting > 0:  # there is something to read
                time.sleep(0.1)
                read_buffer = self.ser.read(self.ser.in_waiting)
                q.put(read_buffer.decode("ascii"))

    def clean_up(self):
        self.ser.close()
        GPIO.cleanup()
