#!/usr/bin/env python

from float_to_int import *
import wave

directory = './Kyma Dx Demo'
basename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_resynthesis'
inFileExtension = 'fl32'
inFilename = f'{directory}/{basename}.{inFileExtension}'
outFileExtension = 'wav'
outFilename = f'{directory}/{basename}.{outFileExtension}'

endianness = 'little'
sampleRate = 48000
bitDepth = 24
sampleWidth = bitDepth // 8
channels = 1

buff = []
with open(inFilename, 'r') as inFile:
    for line in inFile:
        buff.append(float(line.strip()))

with wave.open(outFilename, 'wb') as outFile:
    outFile.setparams((
            channels, # Channels
            sampleWidth, # Sample width
            sampleRate, # Sample rate
            71040, # Total number of sample frames
            'NONE', # Compression type
            'NONE' # Compression name
        ))
    with open(inFilename, 'r') as inFile:
        for line in inFile:
            floatValue = float(line.strip())
            intValue = float_to_int_signed(floatValue, bitDepth)
            encoded = intValue.to_bytes(
                    sampleWidth,
                    byteorder=endianness,
                    signed=True
                )
            outFile.writeframes(encoded)
    outFile.writeframes(b'')

