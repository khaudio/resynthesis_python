#!/usr/bin/env python

# Parse spectral analysis file from Kyma
# 
# Spectral Analysis files are formatted as AIFF files.
# Manually set the sample rate, bit depth, and number of channels.
# Manually set the number of partials, then parse the data after
# the "SSND" chunk in the file, read each sample as frequency data
# to control oscillators at each frequency; one oscillator per
# partial.  Each "kyma frame" is one sample per partial.
# So, for a file with 64 partials at 24-bit, each 3-byte chunk
# represents one control sample per oscillator per "frame".

import collections
import struct
from int_to_float import *

directory = './example_data'
filename = f'{directory}/Sine_1000-0dB_48000 s256.spc'

sampleRate = 48000
bitDepth = 24
sampleWidth = bitDepth // 8
channels = 1
numPartials = 256

controlFrame = collections.deque(maxlen=(numPartials))

with open(filename, 'rb') as f:
    headerFormat = f.read(4)
    if not headerFormat == b'FORM':
        print(f'Not an AIFF file: {headerFormat}')
        exit()
    fileSize = int.from_bytes(f.read(4))
    f.read(14) # Skip channel count
    numSampleFrames = int.from_bytes(f.read(4))
    f.read(2)
    index = 28
    chunkSize = 4
    chunk = b''
    try:
        while chunk != b'SSND':
            chunk = f.read(chunkSize)
            index += chunkSize
        else:
            print(f'SSND chunk found: {chunk}')
            f.read(12) # Skip size metadata
            index += 12
        chunkSize = 6 # 24-bit freq, 24-bit amp
        framePartialIndex = 0
        controlFrameIndex = 0
        while index < fileSize:
            chunk = f.read(chunkSize)
            index += chunkSize
            controlFrame.append((chunk[0:3], chunk[3:6]))
            framePartialIndex += 1
            if framePartialIndex == numPartials:
                controlFramePrintIndex = 0
                for sample in controlFrame:
                    controlFramePrintIndex += 1
                    freq = int.from_bytes(sample[0], 'big', signed=True)
                    amp = int.from_bytes(sample[1], 'big', signed=True)
                    print(controlFramePrintIndex, '\t', freq, amp, end='\n')
                framePartialIndex = 0
                controlFrameIndex += 1
                print('\n')
        else:
            print(f'Parsed {controlFrameIndex} control frames of {numSampleFrames} total {bitDepth}-bit frames')
            print('EOF Reached')

    except KeyboardInterrupt:
        exit()
print('Exiting')
