#!/usr/bin/env python

# Generate audio file with dc offset

import wave

# Set to false to generate negative dc offset signal
positiveOffset = True

sampleRate = 48000
bitDepth = 24
sampleWidth = bitDepth // 8
durationInSeconds = 30
maxAmplitude = ((2 ** (bitDepth  - 1)) - (1 if positiveOffset else 0)) * (1 if positiveOffset else -1)
maxFloatAmplitude = 1.0
numSamples = sampleRate * durationInSeconds

directory = '.'
basename = f'DC_Offset_FullScale_{"Pos" if positiveOffset else "Neg"}_{sampleRate}_{bitDepth}'
outFileExtension = 'wav'
outFilename = f'{directory}/{basename}.{outFileExtension}'
sampleData = maxAmplitude.to_bytes(sampleWidth, byteorder='little', signed=True)

with wave.open(outFilename, 'wb') as outFile:
    outFile.setparams((
            1, # Channels
            3, # Sample width
            sampleRate, # Sample rate
            numSamples, # Total number of sample frames
            'NONE', # Compression type
            'NONE' # Compression name
        ))
    for i in range(numSamples):
        outFile.writeframesraw(sampleData)
    outFile.writeframes(b'')

