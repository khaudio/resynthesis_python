#!/usr/bin/env python

from interpret_freq_and_amp_float_values import *
from feed_sos import *

inDirectory = './Kyma Dx Demo'
outDirectory = './Kyma Dx Demo/partials'
ampBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_amps'
freqBasename = f'Kyma_dx_demo_001_48000_24_s128_71040_frames_freqs'
partialBasename = 'Kyma_dx_demo_001_48000_24_s128_71040_frames_partialIndex'

numPartials = 128

inFileAmpExtension = 'amp'
inFileFreqExtension = 'freq'
outFileExtension = 'fl32'

ampFilename = f'{inDirectory}/{ampBasename}.{inFileAmpExtension}'
freqFilename = f'{inDirectory}/{freqBasename}.{inFileFreqExtension}'


def increment_partial_index(partialIndex, numPartials):
    partialIndex += 1
    partialIndex %= numPartials
    return partialIndex


# Create empty partial files
for i in range(numPartials):
    with open(f'{outDirectory}/{partialBasename}_{i}.{outFileExtension}', 'w') as f:
        f.write('')

partialIndex = 0
partialFiles = []
for i in range(numPartials):
    f = open(f'{outDirectory}/{partialBasename}_{i}.{outFileExtension}', 'a')
    partialFiles.append(f)

for amp, freq in feed_float_values_from_files(ampFilename, freqFilename):
    partialFiles[partialIndex].write(f'{amp}\t{freq}\n')
    partialIndex = increment_partial_index(partialIndex, numPartials)

# Close partial files
for f in partialFiles:
    f.close()

