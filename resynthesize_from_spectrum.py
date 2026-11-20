#!/usr/bin/env python

from sum_of_sines import *
from conversions import *

directory = './example_data/byte_clear'
baseFilename = 'carla_iam_original'

inFileAmps = f'{baseFilename}_amp'
inFileFreqs = f'{baseFilename}_freq'
inFileExtension = 'aif'
inFilenameAmps = f'{directory}/{inFileAmps}.{inFileExtension}'
inFilenameFreqs = f'{directory}/{inFileFreqs}.{inFileExtension}'
outFilename = f'{directory}/{baseFilename}_resynthesis.{inFileExtension}'

# Set to True if spectrum file is log, False for linear spectrum
logSpectrum = True

# Set logScale to adjust pitch
logScale = 1.0

# Set linearScale to adjust frequency offset
linearScale = 1.0

# Number of partials must match the input spectrum
# numPartials must equal the spectral frame duration in samples
numPartials = 128

# Whether to quantize oscillator frequency to nearest frequency bin
# when working with log spectra
quantize = False

# Input data sample rate, as determined by how the spectrum was captured
inputSampleRate = 44100

# Output sample rate to resynthesize
outputSampleRate = 44100

print('Resynthesizing...')

amps = np.array(list(a[0] for a in sf.read(inFilenameAmps, dtype='float64', always_2d=True)[0]), dtype=np.float64)
freqs = np.array(list(f[0] for f in sf.read(inFilenameFreqs, dtype='float64', always_2d=True)[0]), dtype=np.float64)
outputBuff = np.array([], dtype=np.float64)
partialIndex = 0
oscBank = OscillatorBank(sampleRate=outputSampleRate, numOscillators=numPartials, allowDC=False)
for ampScalar, freqScalar in zip(amps, freqs):
    oscBank.oscillators[partialIndex].amplitude = ampScalar

    # Pitch scale
    if logSpectrum:
        freqScalar *= logScale
    else:
        freqScalar = linear_freq_scalar_to_log(freqScalar) * logScale

    # Frequency offset
    freqScalar = log_freq_scalar_to_linear(freqScalar, quantize=quantize) * linearScale

    # Set osc frequency with linearized frequency scalar
    oscBank.oscillators[partialIndex].frequency = get_frequency_from_linear_scalar(freqScalar, inputSampleRate)

    outputBuff = np.append(outputBuff, oscBank.get_osc_sum(1))
    partialIndex = increment_partial_index(partialIndex, numPartials)

print(f'Writing file...')
sf.write(outFilename, outputBuff, outputSampleRate, format='aiff', subtype="FLOAT")

print(f'{len(outputBuff)} samples writen to {outFilename}')

