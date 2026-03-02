#!/usr/bin/env python

import numpy as np
import soundfile as sf


epsilon = 1e-15


def scale_gain_2_13(value):
    return value * (32 / 15)


def log_magnitude(buff, epsilon=0.0):
    return ((np.log2(np.abs(buff) + epsilon)) / 32.0)


def log_to_linear(buff):
    return np.power(2.0, 32.0 * buff)


def linear_to_log(buff, epsilon=0.0):
    return np.log2(buff + epsilon)


def convert_lin_float_to_freq(value, sampleRate):
    return value * (sampleRate * 0.5)


def amp_to_power(amp):
    return amp * amp


def power_to_amp(power):
    return np.sqrt(power)


def power_to_decibels(power, epsilon=0.0):
    return 10.0 * np.log10(power + epsilon)


def decibels_to_power(decibels):
    return np.power(10.0, decibels / 10.0)


def amp_to_decibels(amp, epsilon=0.0):
    return 20.0 * np.log10(amp + epsilon)


def decibels_to_amp(decibels):
    return np.power(10.0, decibels / 20.0)


def minimum_freq(sampleRate):
    return sampleRate / (2 ** 16)


def linear_to_log_freq_value(lin_val, sampleRate, margin=epsilon):
    '''
    Convert linear value to log value,
    expressed as amplitude in spectra.
    sampleRate should be determined by the input
    data, not the output sample rate.
    '''
    freq = lin_val * (sampleRate * 0.5)
    minFreq = minimum_freq(sampleRate)
    freq = np.maximum(freq, minFreq)
    if freq <= minFreq + margin:
        return 0.0
    return (np.log2(freq) - np.log2(minFreq)) / 15.0


def quantize_frequency(freq, sampleRate):
    '''
    Quantize frequency to nearest bin estimate
    '''
    step = sampleRate / (2 ** 16)
    return round((freq / (step))) * step


def log_to_linear_freq_value(logValue, sampleRate, quantize=False, margin=epsilon):
    '''
    Convert log value to linear value,
    expressed as amplitude in spectra.
    sampleRate should be determined by the input
    data, not the output sample rate.
    '''
    minFreq = minimum_freq(sampleRate)
    freq = minFreq * (2.0 ** (15.0 * logValue))
    nyquist = (sampleRate * 0.5)
    if freq <= minFreq + margin:
        return 0.0
    elif quantize:
        return quantize_frequency(freq, sampleRate) / nyquist
    else:
        return freq / nyquist


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
