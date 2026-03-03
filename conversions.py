#!/usr/bin/env python

import numpy as np
import soundfile as sf


maxBinIndex = np.power(2, 16)
octaveRange = np.log2(maxBinIndex) - 1.0
logScale = np.float64(1.0 / octaveRange)
epsilon = np.float64(1e-15)


def scale_gain_2_13(value):
    return value * np.float64(32.0 / 15.0)


def log_magnitude(value, epsilon=0.0):
    return ((np.log2(np.abs(value) + epsilon)) / 32.0)


def log_to_linear(value):
    return np.power(2.0, 32.0 * value)


def linear_to_log(value, epsilon=0.0):
    return np.log2(value + epsilon)


def amplitude_to_power(amplitude):
    return np.power(amplitude, 2.0)


def power_to_amplitude(power):
    return np.sqrt(power)


def power_to_decibels(power, epsilon=0.0):
    return 10.0 * np.log10(power + epsilon)


def decibels_to_power(decibels):
    return np.power(10.0, decibels / 10.0)


def amplitude_to_decibels(amplitude, epsilon=0.0):
    return 20.0 * np.log10(amplitude + epsilon)


def decibels_to_amplitude(decibels):
    return np.power(10.0, decibels / 20.0)


# def minimum_freq(sampleRate):
#     return sampleRate / (2 ** 16)


# def linear_to_log_freq_value(value: np.float64, sampleRate, margin=epsilon):
#     '''
#     Convert linear frequency coefficient expressed as amplitude to log
#     '''
#     freq = value * (sampleRate * 0.5)
#     minFreq = minimum_freq(sampleRate)
#     freq = np.maximum(freq, minFreq)
#     if freq <= minFreq + margin:
#         return 0.0
#     return (np.log2(freq) - np.log2(minFreq)) / 15.0


# def log_to_linear_freq_value(value: np.float64, sampleRate, quantize=False, margin=epsilon):
#     '''
#     Convert log frequency coefficient expressed as amplitude to linear
#     '''
#     minFreq = minimum_freq(sampleRate)
#     freq = minFreq * (2.0 ** (15.0 * value))
#     nyquist = (sampleRate * 0.5)
#     if freq <= minFreq + margin:
#         return 0.0
#     elif quantize:
#         binIndex = sampleRate / (2 ** 16)
#         return (round((freq / (binIndex))) * binIndex) / nyquist
#     else:
#         return freq / nyquist


def linear_freq_scalar_to_log(linearValue):
    if linearValue <= 0:
        return 0
    return (logScale * np.log2(linearValue * maxBinIndex))


def log_freq_scalar_to_linear(logValue, quantize=False):
    binIndex = np.power(2.0, 15.0 * logValue)
    binIndex = round(binIndex) if quantize else binIndex
    if (binIndex < 1) or (logValue <= 0):
        return 0
    return binIndex / maxBinIndex


def get_frequency_from_linear_scalar(linearValue, sampleRate):
    '''
    Conversion to oscillator frequency from linear frequency scalar
    expressed as amplitude
    '''
    return linearValue * (sampleRate * 0.5)


def get_frequency_from_log_scalar(logValue, sampleRate, quantize=False):
    '''
    Conversion to oscillator frequency from log frequency scalar
    expressed as amplitude
    
    quantize rounds the frequency to the nearest bin
    '''
    binIndex = np.power(2, (logValue / logScale))
    binIndex = round(binIndex) if quantize else binIndex
    if (binIndex < 1) or (logValue <= 0):
        return 0
    return binIndex * (sampleRate / maxBinIndex)


def get_spectral_data_from_st_file(filename):
    data = sf.read(filename, dtype='float64', always_2d=True)[0]
    for amp, freq in data:
        yield amp[0], freq[0]


def read_file_in_spectral_frames(filename, numPartials):
    yield from sf.blocks(
            filename,
            blocksize=numPartials,
            overlap=0, 
            dtype='float64',
            always_2d=False
    )


def increment_partial_index(partialIndex, numPartials):
    return (partialIndex + 1) % numPartials


