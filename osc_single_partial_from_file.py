#!/usr/bin/env python

from oscillator import *

numPartials = 128
selectedPartial = 6

sampleRate = 48000

directory = './Kyma Dx Demo'
partialSubDirectory = f'{directory}/partials'
partialBasename = 'Kyma_dx_demo_001_48000_24_s128_71040_frames_partialIndex'

fileExtension = 'fl32'
partialFilename = f'{partialSubDirectory}/{partialBasename}_{selectedPartial}.{fileExtension}'
outFilename = f'{partialSubDirectory}/{partialBasename}_{selectedPartial}_resynthesis.{fileExtension}'

# Initialize oscillator to DC
osc = Oscillator(sampleRate, 0.0, 1.0, 0.0)

# Override frequency to test amplitudes
osc.frequency = 1000.0

with open(outFilename, 'w') as outFile:
    with open(partialFilename, 'r') as inFile:
        for line in inFile:
            osc.amplitude, osc.frequency = (float(value) for value in line.split())
            buff = osc(numPartials) # Oscillate until control data is loaded on the next frame for this partial

            for sample in buff:
                outFile.write(f'{sample}\n')

