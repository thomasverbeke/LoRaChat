""" LoRa Sender Side 
    This part of the code starts as a sender
"""

import serial
import time

ser = serial.Serial(
	port = "/dev/ttyAMA0",
	baudrate=57600,
	bytesize = serial.EIGHTBITS,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	timeout=3.0)

print("start")
# configuration, set watchdog for 50s and pause mac
ser.write("radio get mod\r\n")
ser.readline()

ser.write("radio set wdt 50000\r\n")
ser.readline()

ser.write("mac pause\r\n")
ser.readline()

ser.write("mac get status\r\n")
ser.readline()

while True:
    print('new loop')
    print('set freq?')
    ser.write("radio set freq 868100000\r\n")
    print ser.readline()
    
    # send HELLO
    print 'send hello (ok, radio_tx_ok)'
    ser.write("radio tx 48656c6C6F\r\n")
    print ser.readline() # ok
    print ser.readline() # radio_tx_ok

    # put in continous reception mode
    print 'put in cont reception mode'
    ser.write("radio rx 0\r\n")
    print ser.readline()
    
    resp = ser.readline()
    # if busy then try again in next loop

    # keep reading until message diff from ''
    
    while resp == '':
        resp = ser.readline()

    while resp == '\r\n':
        resp = ser.readline()
         
    print resp

    # sleep 4 seconds
    print 'sleep'
    time.sleep(5)
    # print ser.readline()
    # print ser.readline()
    # print '~~end of reception mode'
