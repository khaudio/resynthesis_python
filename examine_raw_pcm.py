#!/usr/bin/env python

# Examine raw pcm data
# wav == little endian
# aiff = big endian

import struct
from int_to_float import *

directory = './Kyma Dx Demo'
basename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_amps'

length = 71040

toFloat = True
sampleRate = 48000
bitDepth = 24
sampleWidth = bitDepth // 8
endianness = 'big'
chunkSize = sampleWidth
dataSize = length * sampleWidth

endianText = ''
if endianness == 'big':
    endianText = 'BE'
elif endianness == 'little':
    endianText = 'LE'
else:
    raise ValueError('Unknown endianness')

inFileExtension = 'pcm'
inFilename = f'{directory}/{basename}.{inFileExtension}'

outFileExtension = 'fl32' if toFloat else f'int{bitDepth}'
outFilename = f'{directory}/{basename}.{outFileExtension}'

index = 0
with open(outFilename, 'w') as outFile:
    with open(inFilename, 'rb') as inFile:
        while index < dataSize:
            chunk = inFile.read(chunkSize)
            index += chunkSize
            converted = (
                        int24_to_float(chunk, endianness)
                        if toFloat
                        else int.from_bytes(chunk, byteorder=endianness, signed=True)
                    )
            outFile.write(f'{converted}\n')

