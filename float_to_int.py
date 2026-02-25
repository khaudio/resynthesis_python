#!/usr/bin/env python


def float_to_int_signed(floatValue, bitDepth):
    
    # Clipping not enabled
    
    return round(floatValue * ((2 ** (bitDepth - 1)) - 1)) # Ignore extra int(1) on negative

