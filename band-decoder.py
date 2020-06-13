from enum import Enum
import serial

class Band(Enum):
	TWO_M = '2m'
	SEVENTY_CM = '70cm'
	UNKNOWN = 'unknown'

	def __str__(self):
		return self.value

def getByte():
	return ord(ser.read())

def getMessage():
	message=[]
	preambleRead = False
	messageRead = False

	last=0
	current=0
	
	while not messageRead:
		last = current
		current = getByte()
		if current & last == 0xfe:
			preambleRead = True
			continue
		
		if current == 0xfd and preambleRead:
			messageRead = True
			continue

		if preambleRead:
			message.append(current)
	return message

def getBcdDigits(bcd):
	for digit in bcd:
		for val in (digit >> 4, digit & 0xf):
			if val == 0xf:
				return
			yield val

def getFrequencyInHz(message):
	d = list(getBcdDigits(msg[3:8]))
	return d[8] * 1000000000  + d[9] * 100000000  + d[6] * 10000000 + d[7] * 1000000 + d[4] * 100000 + d[5] * 10000 + d[2] * 1000 +  d[3] * 100 + d[0] * 10 + d[1]

def getBand(frequencyInHz):
	if frequencyInHz >= 144000000 and frequencyInHz <= 146000000:
		return Band.TWO_M
	elif frequencyInHz >= 430000000 and frequencyInHz <= 440000000:
		return Band.SEVENTY_CM
	else:
		return Band.UNKNOWN

ser = serial.Serial('/dev/tty.usbserial-24112016A', 19200, timeout=None)

currentBand=Band.UNKNOWN

ser.write(bytearray([0xfe, 0xfe, 0x60, 0x01, 0x03, 0xfd]))

while True:
	msg = getMessage()
#	print ("New message: " + '[{}]'.format(', '.join(hex(x) for x in msg)))
	if msg[2] == 0x00 or (msg[2] == 0x03 and len(msg) == 8):
		band = getBand(getFrequencyInHz(msg))
		if band != currentBand:
			print("Switched to " + str(band) + " band")
			currentBand = band
#		print('{:,}'.format(getFrequencyInHz(msg)) + ' MHz')
