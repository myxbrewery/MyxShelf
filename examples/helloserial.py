#!/usr/bin/env python   
import time
import serial
              
ser = serial.Serial(            
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
         
while 1:
    ser.write(b'0')
    print('0 sent')
    line = ser.readline()
    print(line)
