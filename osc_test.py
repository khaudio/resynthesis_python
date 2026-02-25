#!/usr/bin/evn python

from oscillator import *
from illustrate_float_waveform import *
from sum_of_sines import *
import soundfile as sf

sampleRate = 48000
bufferSizeInSamples = sampleRate * 4

numOscillators = 4
freq = 440.0
amplitude = 0.25


def write_float32_wav(filename, floatList, samplerate):
    audio = np.asarray(floatList, dtype=np.float32)
    sf.write(filename, audio, samplerate, subtype="FLOAT")


buff = [0 for _ in range(bufferSizeInSamples)]

harmonicIndex = 1
oscBank = OscillatorBank(sampleRate, numOscillators)
for i in range(numOscillators):
    oscBank.set_frequency(i, freq * harmonicIndex)
    oscBank.set_amplitude(i, amplitude)
    harmonicIndex += 1

for i in range(numOscillators):
    buff += oscBank.get_osc_data(i, bufferSizeInSamples)

# divisor = bufferSizeInSamples
# buffChunkSize = int(bufferSizeInSamples / divisor)
# osc = Oscillator(sampleRate, 1000.0, 1.0, 0.0)
# for i in range(bufferSizeInSamples):
#     subBuff = osc(buffChunkSize)
#     for j in range(buffChunkSize):
#         buff[(i * buffChunkSize) + j] = subBuff[j]

write_float32_wav('test.wav', buff, sampleRate)
