""" LoRa Chat

	Author: Thomas Verbeke

	Goal: Make a point to point Chat application over LoRa (modulation only) 
	The application talks to the RN2483 over UART. The firmware running on the RN2483 is not open source so 
	the only way to interact with the SX1276 by semtech is using the UART frames made available by microchip.
	
	The following parameters can be set/get (http://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf)

	mod - lora or fsk, default is lora
	freq - frequency, default is 868 100 000
	pwr - output power, max is 14, default 1
	sf - spreading factor, default is sf12
	crc - use crc or not, default is on
	iqi - invert iq, default is off
	cr - coding rate, default is 4/5
	wdt - timeout for watch dog timer, 15 000
	sync - set sync word - ?
	bw - bandwidth - default is 125
	snr - comm snr value - default is -128

	The RN2483 basically consist out of a PIC18LF46K22 which implement a LoRaWAN stack and communicates with 
	the semtech SX1276 chip over SPI. This SPI can be read out from the test soldering pads at the back of the
	chip (numbers 8,10 and 11). 

	The SX1276 is made to serve as an end-device and is thus not ideally suited for use as a concentrater node.
	For that there is the more expensive multi-modem SX1301 transciever. Datasheets made available for the SX1301
	are very limited but there is some open source code made available https://github.com/Lora-net/lora_gateway 

	As said before, the goal here is establish reliable point-to-point communication between SX1276 chips, implement
	a basic mac layer and test what the chips are capable of doing in the real world. There are a few cases in which 
	this could prove usefull: drone market for example.

	First check which platform is used, support for linux and windows
	Setup UART
	Setup LoRa device
	let user choose role, 1: receiver; 0: sender
	pauze mac - mac pause\r\n
	put in continuous reception mode - radio rx 0\r\n
	basic mac layer

	BASIC:

	Idea for full duplex communciation: use same principle as defined in LoRaWAN mac layer.
	One of the 2 devices (the receiver) put itself in continuous reception mode. The sender send a message and
	immediately opens a reception window. (Can be extended with 2 reception windows once ADR is implemented).
	This reception window can then be used to receive an ACK, or receive data that is pending. 

	ADDITIONAL FEATURES
				- ACK 
				- Frequency Hopping, switch between frequencies in lookup table to comply with ETSI regulations
				- Adaptive Rate Control, based on SNR switch to different spreading factor
				- Addressing
				- Encryption """

import serial
import sys
import glob

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

#print serial ports
print(serial_ports())

if sys.platform.startswith('win'):
    ser = serial.Serial(
        port = "COM4", 
        baudrate=57600,
        bytesize=serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout=3.0)

elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    ser = serial.Serial(
        port = "/dev/ttyAMA0", 
        baudrate=57600,
        bytesize=serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout=3.0)

#1. CONFIGURATION

print("**Configuration**")
#clear bad previous cmd
ser.write("radio get mod\r\n")
response = ser.readline()

#1.1 WATCHDOG TIMER
ser.write("radio set wdt 50000\r\n")
response = ser.readline()
if response == 'ok\r\n':
    print("<watchdog> Watchdog set at 50s")
else:
    print("<watchdog> Error")

#1.2 MAC 
ser.write("mac get status\r\n")
response = ser.readline()

if response != '0080\r\n': #Pause mac if not paused
    ser.write("mac pause\r\n")

    response = ser.readline()  

    if response == "4294967245\r\n": #The maximum value 4294967295 is returned whenver the LoRaWAN stack functionality is in Idle state and the transceiver can be used without restrictions.
        print("<mac> Idle state")
    elif response == '0\r\n':  #0 is returned when the LoRaWAN stack cannot be paused. 
        print("<mac> LoRaWAN Stack cannot be paused")
    else: #Error
        print("<mac> Response not recognised")
else:
    print("<mac pause> Idle state")

#1.3 CONTINIOUS RECEPTION MODE
ser.write("radio rx 0\r\n")  #put in continuous reception mode; watchdog will still reset after "radio get wdt\r\n"

response = ser.readline()



if response == "ok\r\n":
    print("<radio rx 0> Ok (Continuous Reception Mode activated")
elif response == "busy\r\n":
    print("<radio rx 0> Busy")
else:
    print("<radio rx 0> Error") 


while True:
    msg = ser.readline() #block until new message
    if msg == '':#ignore, whitespace
        pass
    else:
        
        if msg == 'radio_rx  48656C6C6F\r\n':
            print("HELLO")

            ser.write("radio tx 41434b0d0a\r\n")
            response = ser.readline()

            if response == "ok\r\n":
                print("ACK (in hex: 41 43 4b 0d 0a) has been send")
            else:
                print("Error")

            ser.write("radio rx 0\r\n") #and put back into receive mode

            if response == "ok\r\n":
                print("<radio rx 0> Ok (Continuous Reception Mode activated")
            elif response == "busy\r\n":
                print("<radio rx 0> Busy")
            else:
                print("Error")
        else:
            print(msg)
        
        

    