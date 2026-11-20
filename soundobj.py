#!/usr/bin/env python

import soundfile as sf

def parse_soundfile_subtype(subtype):
    match subtype:
        case 'PCM_S8':
            bitDepth = 8
            signed = True
        case 'PCM_16':
            bitDepth = 16
            signed = True
        case 'PCM_24':
            bitDepth = 24
            signed = True
        case 'PCM_32':
            bitDepth = 32
            signed = True
        case 'PCM_U8':
            bitDepth = 8
            signed = False
        case 'FLOAT':
            bitDepth = 32
            signed = None
        case 'DOUBLE':
            bitDepth = 64
            signed = None
        case _:
            raise ValueError(f'Unsupported or invalid subtype: {subtype}')
    return bitDepth, signed, bitDepth // 8


class SoundObj:
    def __init__(self, sampleRate, bitDepth, channels, signed=None):
        self.sampleRate = sampleRate
        self.bitDepth = bitDepth
        self.channels = channels
        self.signed = signed

    @property
    def bitDepth(self):
        return self._bitDepth

    @bitDepth.setter
    def bitDepth(self, bitDepth):
        self._bitDepth = bitDepth
        self._sampleWidth = bitDepth // 8

    @property
    def is_float(self):
        return ((self.bitDepth in (32, 64)) and self.signed is None)

    def set_format(self, soundFileInfo: sf._SoundFileInfo):
        if not isinstance(soundFileInfo, sf._SoundFileInfo):
            raise TypeError('Must be of of type SoundFileInfo')
        self.sampleRate = soundFileInfo.samplerate
        self.bitDepth, self.signed, self.sampleWidth = parse_soundfile_subtype(soundFileInfo.subtype)
        self.channels = soundFileInfo.channels


class SoundFile(SoundObj):
    def __init__(self, filename):
        super().__init__(None for i in range(4))
        self.filename = filename
        self.set_format(sf.info(filename))
        self.data = sf.read(
                filename,
                start=0,
                dtype='float64',
                always_2d=True
            )[0]
        self.numFrames = len(self.data)

    def get_data(self):
        for frame in self.data:
            yield frame

