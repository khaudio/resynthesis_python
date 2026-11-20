#!/usr/bin/env python

from sum_of_sines import *
from conversions import *

import matplotlib.pyplot as plt


# # Wall-E
# logScale, linearScale = 1.2, 0.5

# # Eve
# logScale, linearScale = 0.88, 2.7


# directory = './example_data/Kyma Dx Demo'
# logFileBasename = 'Kyma_dx_demo_001_LogSpect_48000_24_s128_71040_frames_freqs'
# linFileBasename = 'Kyma_dx_demo_001_LinSpect_48000_24_s128_71040_frames_freqs'
# inFileExtension = 'aif'
# logFilename = f'{directory}/{logFileBasename}.{inFileExtension}'
# linFilename = f'{directory}/{linFileBasename}.{inFileExtension}'

# # Set to True if spectrum file is log, False for linear spectrum
# numPartials = 128

# quantize = False

# # Input data sample rate, as determined by how the spectra was captured
# inputSampleRate = 48000

# # Values for first frame
# logFrame = list(read_file_in_spectral_frames(logFilename, numPartials))[0]
# linFrame = list(read_file_in_spectral_frames(linFilename, numPartials))[0]

# # Values for entire file
# logValues = list(v[0] for v in sf.read(logFilename, dtype='float64', always_2d=True)[0])
# linValues = list(v[0] for v in sf.read(linFilename, dtype='float64', always_2d=True)[0])

# for logSampleFreqAmplitude, linSampleFreqAmplitude in zip(logFrame, linFrame):
#     linFreqNative = get_frequency_from_linear_scalar(linSampleFreqAmplitude, inputSampleRate)
#     logFreqNative = get_frequency_from_log_scalar(logSampleFreqAmplitude, inputSampleRate, quantize=quantize)
#     logAmpConverted = linear_freq_scalar_to_log(linSampleFreqAmplitude)
#     linAmpConverted = log_freq_scalar_to_linear(logSampleFreqAmplitude, quantize=quantize)

#     print(f'logSampleFreqAmplitude: {logSampleFreqAmplitude}\tlinSampleFreqAmplitude: {linSampleFreqAmplitude}, logAmpConverted: {logAmpConverted}, linAmpConverted: {linAmpConverted}')
#     print(f'linFreqNative: {linFreqNative}, logFreqNative: {logFreqNative}')
#     # print(f'numStepsOffset: {numStepsOffset}')
#     print('')






class OscBankRenderer:
    def __init__(self, oscBank, numPartials):
        self.oscBank = oscBank
        self.numPartials = numPartials
        self.buffers = [
            np.zeros(numPartials, dtype=np.float64)
            for _ in oscBank.oscillators
        ]
        self.global_index = 0

    def render(self, numSamples):
        output = np.zeros(numSamples, dtype=np.float64)

        for n in range(numSamples):
            partial_index = self.global_index % self.numPartials

            # Update only one oscillator
            osc = self.oscBank.oscillators[partial_index]
            self.buffers[partial_index] = osc(self.numPartials)

            sample_sum = 0.0

            for i in range(self.numPartials):
                offset = (self.global_index - i) % self.numPartials
                sample_sum += self.buffers[i][offset]

            output[n] = sample_sum
            self.global_index += 1

        return output


spcFilename = f'./example_data/carla-in a manner h.spc'

# spcValues = np.array([s[0] for s in sf.read(spcFilename, dtype='float64', always_2d=True)[0]], dtype=np.float64)
# spcLastFrame = spcValues[-128:]

# directory = './example_data'
# outFilename = f'{directory}/carla-in a manner h_resynthesis.aif'

# # Number of partials must match the input spectrum
# numPartials = 124

# # Input data sample rate, as determined by how the spectrum was captured
# inputSampleRate = 44100

# # Output sample rate to resynthesize
# outputSampleRate = 44100

# outputBuff = np.array([], dtype=np.float64)
# partialIndex = 0
# oscBank = OscillatorBank(sampleRate=outputSampleRate, numOscillators=124, allowDC=False)
# print('Resynthesizing...')
# # for amp, hz in extract_values_from_spc(spcFilename):
# # for amp, freq in yield_amp_freq_hz_pairs(spc_file=spcFilename, sample_rate=inputSampleRate, skip_padding=True):
# for amp, hz in yield_amp_freq_hz_pairs(spc_file=spcFilename, sample_rate=inputSampleRate):
#     if partialIndex < 124:
#         oscBank.oscillators[partialIndex].amplitude = amp
#         oscBank.oscillators[partialIndex].frequency = hz
#         outputBuff = np.append(outputBuff, oscBank.get_osc_sum(1))
#     partialIndex = increment_partial_index(partialIndex, 128)
# print(f'Writing file...')
# sf.write(outFilename, outputBuff, outputSampleRate, format='aiff', subtype="FLOAT")

# print(f'{len(outputBuff)} samples writen to {outFilename}')


# # spcFilename = f'./example_data/Sine_1000-0dB_48000 s256.spc'
# # frame = list(read_file_in_spectral_frames(spcFilename, 256))[100]

# # for i, s in enumerate(frame):
# #     print(f'partial index: {i}\tscalar: {s}')



import numpy as np

def decode_candidates(partials):

    candidates = {}

    # raw
    candidates["raw"] = partials

    # abs
    candidates["abs"] = np.abs(partials)

    # exponential (log amplitude hypothesis)
    candidates["exp"] = np.exp(partials)

    # exp scaled
    candidates["exp_20"] = np.exp(partials * 20)

    # dB decode
    candidates["db"] = 10 ** (partials / 20)

    # signed exp
    candidates["signed_exp"] = np.sign(partials) * np.exp(np.abs(partials))

    # square
    candidates["square"] = partials ** 2

    # sqrt
    candidates["sqrt"] = np.sqrt(np.abs(partials))

    candidates["exp2"] = np.exp2(partials)

    candidates["log1p"] = np.log1p(np.abs(partials))

    mant = np.floor(partials)
    frac = partials - mant

    freq = 2 ** mant
    amp = frac
    print(f'mantissa packed freq, amp: {freq}\t{amp}')

    return candidates


def spectral_score(matrix):

    # energy stability across frames
    energy = np.sum(matrix, axis=1)
    energy_var = np.std(energy)

    # sparsity (spectra usually sparse)
    sparsity = np.mean(matrix < np.percentile(matrix, 90))

    # peak consistency
    peaks = np.argmax(matrix, axis=1)
    peak_var = np.std(peaks)

    score = (1/(1+energy_var)) + sparsity + (1/(1+peak_var))

    return score


def test_decoders(frames):

    partials = frames[:, :252]

    candidates = decode_candidates(partials)

    scores = {}

    for name, decoded in candidates.items():

        decoded = np.nan_to_num(decoded)
        decoded = np.abs(decoded)

        score = spectral_score(decoded)

        scores[name] = score

    return sorted(scores.items(), key=lambda x: -x[1])


def inspect_peaks(matrix, n=10):

    peaks = np.argmax(matrix, axis=1)

    unique, counts = np.unique(peaks, return_counts=True)

    order = np.argsort(counts)[::-1]

    return list(zip(unique[order][:n], counts[order][:n]))


# frames = 

results = test_decoders(frames)

for r in results:
    print(r)

best = results[0][0]

decoded = decode_candidates(frames[:, :252])[best]

print(inspect_peaks(decoded))

