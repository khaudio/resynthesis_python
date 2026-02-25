#!/usr/bin/env python

# Interpret float values as frequency control data
# by multiplying each by halfSampleRate

import math


directory = './Kyma Dx Demo'
ampBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_amps'
freqBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_freqs'

inFileExtension = 'fl32'
outFileAmpExtension = 'amp'
inFilenameAmp = f'{directory}/{ampBasename}.{inFileExtension}'
outFilenameAmp = f'{directory}/{ampBasename}.{outFileAmpExtension}'
outFileFreqExtension = 'freq'
inFilenameFreq = f'{directory}/{freqBasename}.{inFileExtension}'
outFilenameFreq = f'{directory}/{freqBasename}.{outFileFreqExtension}'

sampleRate = 48000

# Multiplier to obtain frequency values
halfSampleRate = sampleRate * 0.5


def log_magnitude(value):
    return abs(math.log2(value ** 2) / 64)


def yield_amp_floats(filename, linToLog=False):
    with open(filename, 'r') as f:
        for line in f:
            if linToLog:
                yield (log_magnitude(float(line.strip())) * (32 / 15))
            else:
                yield float(line.strip())


def yield_freq_floats(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield float(line.strip()) * halfSampleRate


with open(outFilenameAmp, 'w') as outFileAmp:
    with open(inFilenameAmp, 'r') as inFileAmp:
        for line in inFileAmp:
            value = float(line.strip())

            # # Amplitudes to log
            # value = log_magnitude(value)
            # value *= (32 / 15) # Gain

            outFileAmp.write(f'{value}\n')

with open(outFilenameFreq, 'w') as outFileFreq:
    with open(inFilenameFreq, 'r') as inFileFreq:
        for line in inFileFreq:
            value = float(line.strip())

            # Get freq values
            value *= halfSampleRate

            outFileFreq.write(f'{value}\n')

