import mido
import numpy as np
import sounddevice as sd
from math import sin, pi

SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2
SAMPLE_MAX = (2**8)**SAMPLE_WIDTH//2-1

inputnames = mido.get_input_names()
print("\n".join(inputnames))

if len(inputnames) == 0:
	exit(0)

inport = mido.open_input(inputnames[0])

def sine(frequency, duration):
	l = []
	for i in range(SAMPLE_RATE*duration):
		v = sin(2*pi*i/SAMPLE_RATE*frequency)*SAMPLE_MAX
		l.append(int(v))
	return l

bytestream = None

def callback(outdata, frames, time, status):
	global bytestream
	if status:
		print(status)
	outdata[:] = bytestream

CHUNK = SAMPLE_RATE

pa = pyaudio.PyAudio()

print('\n'.join([y['name']
	for y in [pa.get_device_info_by_index(x)
	for x in range(pa.get_device_count())]]))

stream = pa.open(
	format=pa.get_format_from_width(width=SAMPLE_WIDTH),
	channels=1,
	rate=SAMPLE_RATE,
	output=True,
	#frames_per_buffer=CHUNK,
	stream_callback=playingCallback)

stream.start_stream()

while stream.is_active():
	for msg in inport.iter_pending():
		print(msg)

	s = sine(440, 1)
	bytestream = np.asarray(s, dtype=np.int16)#
	# sounddevice takes care of that for us: .tobytes()
	# This blocks, using callbacks instead: stream.write(bytestream)



stream.stop_stream()
stream.close()

pa.terminate()
