import pyaudio
import numpy as np
import random


Sinefreq = {'A':181.63, 'B':192.43, 'C':203.88, 'D':216.00, 'E':228.45,
			'F':242.45, 'G':261.63, 'H':277.18, 'I':293.66, 'J':311.15,
			'K':329.63, 'L':349.23, 'M':369.99, 'N':372.68, 'O':375.02,
			'P':392.00, 'Q':440.00, 'R':415.30, 'S':466.16, 'R':493.88,
			'S':499.23, 'T':500.25, 'U':510.34, 'V':520.45, 'W':550.93,
			'X':580.88, 'Y':600.32, 'Z':660.00}

def beepmaker(f):
	if f not in Sinefreq.values():
		f = random.choice(list(Sinefreq.values()))

	print("Sound of sine frequency:", f)

	p = pyaudio.PyAudio()

	volume = 0.5     # range [0.0, 1.0]
	fs = 44100       # sampling rate, Hz, must be integer
	duration = 3.0   # in seconds, may be float
	#f is the sine frequency, Hz, may be float

	# generate samples, note conversion to float32 array
	samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

	# for paFloat32 sample values must be in range [-1.0, 1.0]
	stream = p.open(format=pyaudio.paFloat32,
	                channels=1,
	                rate=fs,
	                output=True)

	# play. May repeat with different volume values (if done interactively) 
	stream.write(volume*samples)

	stream.stop_stream()
	stream.close()

	p.terminate()


beepmaker(181.63)