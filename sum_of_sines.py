#!/usr/bin/env python

from oscillator import *
from illustrate_float_waveform import *
from multiprocessing import Queue
import threading

class OscillatorBank:
    def __init__(self, sampleRate, numOscillators, allowDC=False):
        self.sampleRate = sampleRate
        self.numOscillators = numOscillators
        self.oscillators = []
        for i in range(numOscillators):
            self.oscillators.append(Oscillator(sampleRate, frequency=0, amplitude=0, allowDC=allowDC))

    def set_frequency(self, oscillatorIndex, frequency):
        self.oscillators[oscillatorIndex].frequency = frequency
    
    def set_amplitude(self, oscillatorIndex, amplitude):
        self.oscillators[oscillatorIndex].amplitude = amplitude
    
    def get_osc_data(self, oscillatorIndex, numSamples):
        return self.oscillators[oscillatorIndex](numSamples)

    def get_osc_sum(self, numSamples):
        return np.sum([oscillator(numSamples) for oscillator in self.oscillators], axis=0)

class MultithreadedOscillatorBank(OscillatorBank):
    def __init__(self, sampleRate, numOscillators, numThreads):
        super().__init__(sampleRate, numOscillators)
        self.threads = []
        self.freqQueues = []
        self.ampQueues = []
