#!/usr/bin/env python

from sum_of_sines import *
from conversions import *

directory = './example_data/Kyma Dx Demo'
inFileBasenameAmps = 'Kyma_dx_demo_001_LogSpect_48000_24_s128_71040_frames_amps'
inFileBasenameFreqs = 'Kyma_dx_demo_001_LogSpect_48000_24_s128_71040_frames_freqs'
inFileExtension = 'aif'
inFilenameAmps = f'{directory}/{inFileBasenameAmps}.{inFileExtension}'
inFilenameFreqs = f'{directory}/{inFileBasenameFreqs}.{inFileExtension}'
outFilename = f'{directory}/Kyma_dx_demo_001_LogSpect_48000_24_s128_71040_frames_resynthesis.{inFileExtension}'

# Set to True if spectrum file is log, False for linear spectrum
logSpectrum = True

# Number of partials must match the input spectrum
numPartials = 128

# Whether to quantize oscillator frequency to nearest frequency bin
# when working with log spectra
quantize = False

# Input data sample rate, as determined by how the spectrum was captured
inputSampleRate = 48000

# Output sample rate to resynthesize
outputSampleRate = 48000

print('Resynthesizing...')

amps = np.array(list(a[0] for a in sf.read(inFilenameAmps, dtype='float64', always_2d=True)[0]), dtype=np.float64)
freqs = np.array(list(f[0] for f in sf.read(inFilenameFreqs, dtype='float64', always_2d=True)[0]), dtype=np.float64)
outputBuff = np.array([], dtype=np.float64)
partialIndex = 0
oscBank = OscillatorBank(sampleRate=outputSampleRate, numOscillators=numPartials, allowDC=False)
for ampScalar, freqScalar in zip(amps, freqs):
    oscBank.oscillators[partialIndex].amplitude = ampScalar
    oscBank.oscillators[partialIndex].frequency = (
            get_frequency_from_log_scalar(freqScalar, inputSampleRate, quantize=quantize)
            if logSpectrum
            else get_frequency_from_linear_scalar(freqScalar, inputSampleRate)
        )
    outputBuff = np.append(outputBuff, oscBank.get_osc_sum(1))
    partialIndex = increment_partial_index(partialIndex, numPartials)
sf.write(outFilename, outputBuff, outputSampleRate, format='aiff', subtype="FLOAT")

print(f'{len(outputBuff)} samples writen to {outFilename}')

