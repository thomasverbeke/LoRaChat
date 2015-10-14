# LoRaChat
A point to point mac implementation for the RN2483

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
	
	ACK 
	Frequency Hopping, switch between frequencies in lookup table to comply with ETSI regulations
	Adaptive Rate Control, based on SNR switch to different spreading factor
	Addressing
	Encryption
