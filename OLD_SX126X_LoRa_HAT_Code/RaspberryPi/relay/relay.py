#!/usr/bin/python
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
import serial
import time
import sys    

M0 = 22
M1 = 27

'''

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

'''


CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']
RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']

r_buff = ""
delay_temp = 1

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(M0,GPIO.OUT)
GPIO.setup(M1,GPIO.OUT)

GPIO.output(M0,GPIO.LOW)
GPIO.output(M1,GPIO.HIGH)
time.sleep(1)

ser = serial.Serial("/dev/ttyS0",9600)
ser.flushInput()
print("Press \033[1;32mCtrl+C\033[0m to exit")
try :
    if ser.isOpen() :
        print("It's setting RELAY mode")
        ser.write(CFG_REG[0])
        while True :
            if ser.inWaiting() > 0 :
                time.sleep(0.1)
                r_buff = ser.read(ser.inWaiting())
                if r_buff == RET_REG[0] :
                    print("RELAY mode was actived")
                    GPIO.output(M1,GPIO.LOW)
                    time.sleep(0.01)
                    r_buff = ""
                if r_buff != "" :
                    print("receive a RELAY message:")
                    print(r_buff)
                    r_buff = ""
            delay_temp += 1
            if delay_temp > 400000 :
                print('send message')
                ser.write("This is a RELAY message\r\n".encode())
                delay_temp = 0
except :
    if ser.isOpen() :
        ser.close()
        GPIO.cleanup()
