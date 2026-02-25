#!/usr/bin/env python

import numpy as np
import soundfile as sf

def write_float32_wav(filename, floatList, samplerate):
    audio = np.asarray(floatList, dtype=np.float32)
    sf.write(filename, audio, samplerate, subtype="FLOAT")

