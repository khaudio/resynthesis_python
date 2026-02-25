#!/usr/bin/env python

def feed_float_values_from_files(ampFile, freqFile):
    with open(ampFile, 'r') as amps:
        with open(freqFile, 'r') as freqs:
            for a, f in zip(amps, freqs):
                yield float(a.strip()), float(f.strip())
