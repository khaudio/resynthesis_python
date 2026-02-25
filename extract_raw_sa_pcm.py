#!/usr/bin/env python

# Extract raw pcm data from kyma spectral analysis file

directory = './example_data'
filename = f'{directory}/Sine_1000-0dB_48000 s256.spc'

with open(filename, 'rb') as infile:
    header = infile.read(22520)
    data = infile.read(157448)

    with open(f'{directory}/Sine_1000-0dB_48000.sapcm', 'wb') as outfile:
        outfile.write(data)

print('Done')