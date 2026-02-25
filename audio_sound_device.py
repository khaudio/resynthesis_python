#!/usr/bin/env python

import sounddevice as sd
import numpy as np

sampleRate = 48000
bitDepth = 24
channels = 1

if bitDepth == 24:
    dtype = np.int24
else:
    dtype = np.int16
    