#!/usr/bin/env python

import numpy as np
import soundfile as sf


fftSize = np.power(2, 16)
nyquistBin = fftSize // 2
octaveRange = np.log2(nyquistBin)
logScale = np.float64(1.0 / octaveRange)
ampExpBase = np.exp(np.e, np.e)
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


def linear_freq_scalar_to_log(linearValue):
    linearValue = max(linearValue, 0.0)
    return (logScale * np.log2(linearValue * nyquistBin)) if linearValue else 0


def log_freq_scalar_to_linear(logValue, quantize=False):
    binIndex = np.power(2.0, (logValue * octaveRange))
    binIndex = round(binIndex) if quantize else binIndex
    if (binIndex < 1) or (logValue <= 0.0):
        return 0
    return (binIndex / nyquistBin)


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
    binIndex = np.power(2.0, (logValue * octaveRange))
    binIndex = round(binIndex) if quantize else binIndex
    if (binIndex < 1) or (logValue <= 0.0):
        return 0
    return binIndex * (sampleRate / fftSize)


def get_lin_scalar_from_frequency(frequency, sampleRate):
    return np.float64(frequency) / (sampleRate * 0.5)


def get_log_scalar_from_frequency(frequency, sampleRate):
    return np.log2((frequency / (sampleRate / fftSize))) / octaveRange




def extract_frame_frequencies_from_spc(spc_frame, sampleRate=44100):
    """
    Extract frequencies in Hz from an SPC frame.
    
    Each 24-bit spectrum value encodes frequency information in bytes 1-2.
    
    Args:
        spc_frame: array-like of 128 spectrum values (24-bit floats in range [-1, 1])
        sampleRate: sample rate in Hz (default 44100)
    
    Returns:
        frequencies: array of 128 frequency values in Hz
    """
    # fftSize = 65536.0
    # nyquistBin = 32768.0
    # octaveRange = 15.0
    
    spc_frame = np.asarray(spc_frame, dtype=np.float64)
    
    # Convert float representation to integer representation
    spectrum_ints = np.int32(spc_frame * 8388608)
    spectrum_ints = np.where(spectrum_ints < 0, spectrum_ints + 0x1000000, spectrum_ints)
    spectrum_ints = spectrum_ints & 0xFFFFFF
    
    # Extract bytes 1-2 (frequency scalar)
    byte12 = spectrum_ints & 0xFFFF
    freq_scalars = byte12 / 65536.0
    
    # Convert log frequency scalar to linear bin index
    bin_indices = np.power(2.0, freq_scalars * octaveRange)
    linear_scalars = bin_indices / nyquistBin
    
    # Convert to Hz
    frequencies = linear_scalars * (sampleRate * 0.5)
    
    return frequencies


def extract_frame_amplitudes_from_spc(spc_frame):
    """
    Extract amplitudes from an SPC frame.
    
    The amplitude is encoded in the spectrum value using an exponential formula
    fitted to SpectrumOnDisk export data.
    
    Args:
        spc_frame: array-like of 128 spectrum values (24-bit floats)
    
    Returns:
        amplitudes: array of 128 amplitude values (non-negative scalars)
    """
    spc_frame = np.asarray(spc_frame, dtype=np.float64)
    
    # Exponential formula: amplitude = 0.00002691 * exp(10.50186 * spectrum)
    amplitudes = 0.00002691 * np.exp(10.50186 * spc_frame)
    
    return amplitudes




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

