#!/usr/bin/env python

import wave
from float_to_int import *
import numpy as np
import soundfile as sf

numPartials = 128
selectedPartial = 6

sampleRate = 48000
bitDepth = 24
sampleWidth = bitDepth // 8
channels = 1
endianness = 'little'

directory = './Kyma Dx Demo'
partialSubDirectory = f'{directory}/partials'
partialBasename = 'Kyma_dx_demo_001_48000_24_s128_71040_frames_partialIndex'

inFileExtension = 'fl32'
outFileExtension = 'wav'
partialFilename = f'{partialSubDirectory}/{partialBasename}_{selectedPartial}_resynthesis.{inFileExtension}'
outFilename = f'{partialSubDirectory}/{partialBasename}_{selectedPartial}_resynthesis.{outFileExtension}'


def write_float32_wav(filename, floatList, samplerate):
    audio = np.asarray(floatList, dtype=np.float32)
    sf.write(filename, audio, samplerate, subtype="FLOAT")


# with wave.open(outFilename, 'wb') as outFile:
#     outFile.setparams((
#             channels, # Channels
#             sampleWidth, # Sample width
#             sampleRate, # Sample rate
#             71040, # Total number of sample frames
#             'NONE', # Compression type
#             'NONE' # Compression name
#         ))
#     with open(partialFilename, 'r') as inFile:
#         for line in inFile:
#             floatValue = float(line.strip())
#             intValue = float_to_int_signed(floatValue, bitDepth)
#             outFile.writeframes(intValue.to_bytes(sampleWidth, byteorder=endianness, signed=True))
#     outFile.writeframes(b'')


floatValues = []
with open(partialFilename, 'r') as inFile:
    for line in inFile:
        floatValue = float(line.strip())
        floatValues.append(floatValue)

write_float32_wav(outFilename, floatValues, sampleRate)
