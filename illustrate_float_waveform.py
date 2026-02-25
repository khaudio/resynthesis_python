#!/usr/bin/env python

def illustrate_float_waveform(buff):
    '''Illustrate float values as waveform in terminal'''
    signalChar = '\u2022'
    lineLength = 40
    halfLineLength = lineLength * 0.5
    for sample in buff:
        spaces = int(((round(sample * halfLineLength) - 1) + halfLineLength))
        line = f'{sample:.4f}' + f'{spaces * ' '}{signalChar}'
        print(line)


def illustrate_float_waveform_gen(buff):
    '''Illustrate float values as waveform in terminal'''
    signalChar = '\u2022'
    lineLength = 40
    halfLineLength = lineLength * 0.5
    for sample in buff:
        spaces = int(((round(sample * halfLineLength) - 1) + halfLineLength))
        line = f'{sample:.4f}' + f'{spaces * ' '}{signalChar}'
        yield line

