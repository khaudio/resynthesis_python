#!/usr/bin/env python

# Basic sine oscillator controlled by float values for frequency and amplitude

import numpy as np

tau = (2 * np.pi)

class Oscillator:
    def __init__( self, samplerate, frequency, amplitude=1.0, radians=0.0, allowDC=False):
        self.__frequency = 0.0
        self.__amplitude = 1.0
        self.sampleRate = samplerate
        self.frequency = frequency
        self.amplitude = amplitude
        self.radians = radians
        self.allowDC = allowDC

    @property
    def amplitude(self):
        return self.__amplitude

    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < 0:
            raise ValueError('Amplitude must be greater than 0.0')
        self.__amplitude = amplitude

    @property
    def sampleRate(self):
        return self.__sampleRate

    @sampleRate.setter
    def sampleRate(self, samplerate):
        self.__sampleRate = samplerate
        self.increment = tau * self.frequency / samplerate
    
    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, frequency):
        self.__frequency = frequency
        self.increment = tau * self.__frequency / self.sampleRate

    def __call__(self, numSamples):
        '''Returns an array of samples'''
        if not self.allowDC and self.frequency == 0.0:
            return np.zeros(numSamples)
        n = np.arange(numSamples)
        samples = (self.amplitude * np.sin(self.radians + n * self.increment))
        self.radians += (self.increment * numSamples)
        self.radians %= tau
        return samples

    def __str__(self):
        stringOutput = (
                f'Sample Rate: {self.sampleRate}'
                + f'\tFrequency: {self.frequency}'
                + f'\tAmplitude: {self.amplitude}'
                + f'\tRadians: {self.radians}'
                + f'\tIncrement: {self.increment}'
            )
        return stringOutput

    def __repr__(self):
        return """stringOutput = (
                f'Sample Rate: {self.sampleRate}'
                + f'\tFrequency: {self.frequency}'
                + f'\tAmplitude: {self.amplitude}'
                + f'\tRadians: {self.radians}'
                + f'\tIncrement: {self.increment}'
            )
        return stringOutput"""

