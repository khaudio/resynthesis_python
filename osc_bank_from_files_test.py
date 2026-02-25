#!/usr/bin/env python

import math
from sum_of_sines import *
from feed_sos import *

sampleRate = 48000
halfSampleRate = sampleRate / 2
numPartials = 128
numOscillators = numPartials
dataType = np.float32

directory = './Kyma Dx Demo'
ampBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_amps'
freqBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_freqs'
outputBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_resynthesis'

inFileAmpExtension = 'amp'
inFileFreqExtension = 'freq'
outFileExtension = 'fl32'

ampFilename = f'{directory}/{ampBasename}.{inFileAmpExtension}'
freqFilename = f'{directory}/{freqBasename}.{inFileFreqExtension}'
outFilename = f'{directory}/{outputBasename}.{outFileExtension}'

def increment_partial_index(partialIndex, numPartials):
    partialIndex += 1
    partialIndex %= numPartials
    return partialIndex

oscBank = OscillatorBank(sampleRate, numOscillators)

partialIndex = 0
outputBuff = []
sampleCount = 0 # Output sample count

for amp, freq in feed_float_values_from_files(ampFilename, freqFilename):
    oscBank.oscillators[partialIndex].amplitude = amp
    oscBank.oscillators[partialIndex].frequency = freq
    sample = sum(osc(1) for osc in oscBank.oscillators)
    partialIndex = increment_partial_index(partialIndex, numPartials)
    outputBuff.append(sample[0])
    sampleCount += 1

with open(outFilename, 'w') as outFile:
    for sample in outputBuff:
        outFile.write(f'{sample}\n')

