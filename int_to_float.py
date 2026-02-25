#!/usr/bin/env python

# Ingest data in chunks of 3 bytes (24 bits) and convert
# to float in range -1.0 to 1.0.

def int24_to_float(chunk, endianness):
    intValue = int.from_bytes(chunk, endianness, signed=True)
    if intValue >= 0:
        return float(intValue) / 8388607.0
    else:
        return float(intValue) / 8388608.0

