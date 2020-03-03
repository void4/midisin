from time import sleep
from math import sin, pi

import numpy as np

import sounddevice as sd
import mido

SAMPLE_RATE = 44100
BLOCK_SIZE = SAMPLE_RATE // 10
SAMPLE_WIDTH = 2
SAMPLE_MAX = (2**8)**SAMPLE_WIDTH//2-1

inputnames = mido.get_input_names()
print("\n".join(inputnames))

if len(inputnames) == 0:
	print("No inputs!")
	exit(1)

inport = mido.open_input(inputnames[0])

def sine(frequency, duration):
	l = []
	for i in range(BLOCK_SIZE):
		v = sin(2*pi*i/SAMPLE_RATE*frequency)*SAMPLE_MAX
		l.append(int(v))
	return l

bytestream = np.zeros(BLOCK_SIZE, dtype=np.int16)

def callback(outdata, frames, time, status):
	global bytestream

	#print(status.output_underflow)

	if len(bytestream) > 0:
		outdata[:len(bytestream)] = bytestream.reshape(BLOCK_SIZE, 1)

		if len(bytestream) < len(outdata):
			missing = (len(outdata) - len(bytestream))
			filler = numpy.zeros(missing, dtype=np.int16)
			outdata[len(bytestream):] = filler

def finished_callback():
	print("DONE")

stream = sd.OutputStream(samplerate=SAMPLE_RATE,
	channels=1,
	dtype=np.int16,
	blocksize=BLOCK_SIZE,
	callback=callback,
	finished_callback=finished_callback)

stream.start()

notes = {}

while stream.active:

	for msg in inport.iter_pending():
		#print(msg)
		#print(msg.type)
		if msg.type == "note_on":
			notes[msg.note] = True
		elif msg.type == "note_off":
			notes[msg.note] = False

	channels = []#np.empty(shape=(0, BLOCK_SIZE), dtype=np.int16)
	for note, active in notes.items():
		if active:
			s = sine(note*10, 1)
			#channel = np.asarray(s, dtype=np.int16)#
			#channels = np.append(channels, channel, axis=0)
			channels.append(s)

	channels = np.asarray(channels, dtype=np.int16)

	#if len(channels) > 0:
	#	print(channels)

	if len(channels) == 0:
		bytestream = np.zeros(BLOCK_SIZE, dtype=np.int16)
	else:
		bytestream = np.mean(channels, axis=0)

	#print(bytestream)
	#sleep(1)
