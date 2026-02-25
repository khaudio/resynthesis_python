#!/usr/bin/env python

# Extract raw pcm data from an audio file

directory = './Kyma Dx Demo'
basename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_amps'
numSampleFrames = 71040
bitDepth = 24
sampleWidth = bitDepth // 8


inFileExtension = 'aif'
inFilename = f'{directory}/{basename}.{inFileExtension}'

outFileExtension = 'pcm'
outFilename = f'{directory}/{basename}.{outFileExtension}'

with open(inFilename, 'rb') as infile:
    header = infile.read(512)
    data = infile.read(numSampleFrames * sampleWidth)

    with open(outFilename, 'wb') as outfile:
        outfile.write(data)

