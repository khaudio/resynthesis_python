#!/usr/bin/env python

from illustrate_float_waveform import *

directory = './Kyma Dx Demo'
basename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_resynthesis'
inFileExtension = 'fl32'
inFilename = f'{directory}/{basename}.{inFileExtension}'
outFileExtension = 'wfm'
outFilename = f'{directory}/{basename}.{outFileExtension}'

chunkSize = 128
chunk = []
index = 0

with open(outFilename, 'w') as outFile:
    with open(inFilename, 'r') as inFile:
        for line in inFile:
            chunk.append(float(line.strip()))
            index += 1
            if index == chunkSize:
                for line in illustrate_float_waveform_gen(chunk):
                    outFile.write(f'{line}\n')
                chunkBuff = []
                index = 0

