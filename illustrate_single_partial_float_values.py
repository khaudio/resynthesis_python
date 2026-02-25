#!/usr/bin/env python

from illustrate_float_waveform import *


numPartials = 128
selectedPartial = 6

directory = './Kyma Dx Demo'
partialSubDirectory = f'{directory}/partials'
partialBasename = 'Kyma_dx_demo_001_48000_24_s128_71040_frames_partialIndex'

inFileExtension = 'fl32'
filename = f'{partialSubDirectory}/{partialBasename}_{selectedPartial}_resynthesis.{inFileExtension}'

buff = []

with open(filename, 'r') as f:
    for line in f:
        buff.append(float(line.strip()))
illustrate_float_waveform(buff)

