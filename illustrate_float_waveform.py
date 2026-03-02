#!/usr/bin/env python

def illustrate_float_sample(sample, fill=' '):
    '''Illustrate float values as waveform in terminal'''
    signalChar = '\u2022'
    lineLength = 40
    halfLineLength = lineLength * 0.5
    spaces = int(((round(sample * halfLineLength) - 1) + halfLineLength))
    return f'{sample:.4f}' + f'{spaces * fill}{signalChar}'


def illustrate_float_waveform(buff, fill=' ', scaled=False):
    '''Illustrate float values as waveform in terminal'''
    signalChar = '\u2022'
    lineLength = 40
    halfLineLength = lineLength * 0.5
    limit = max(abs(sample) for sample in buff)
    for sample in buff:
        spacerValue = sample / (limit if (scaled and limit) else 1.0)
        spaces = int(((round(spacerValue * halfLineLength) - 1) + halfLineLength))
        yield f'{sample:.4f}' + f'{spaces * fill}{signalChar}'

