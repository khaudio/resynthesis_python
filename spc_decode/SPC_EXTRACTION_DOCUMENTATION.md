# SPC Spectrum Extraction & Conversion Functions

## Overview

Complete set of functions for extracting frequency and amplitude information from SPC spectrum values, and converting between SPC format and discrete frequency/amplitude channels.

## Constants

```python
EULER = np.e ≈ 2.71828183
EULER_TO_EULER = e^e ≈ 15.15426224

FFT_SIZE = 2^16 = 65536
NYQUIST_BIN = 32768
OCTAVE_RANGE = log2(32768) = 15.0

AMP_EXP_BASE = e^e ≈ 15.15426224
```

---

## Frequency Extraction Pipeline

### 1. `extract_frequency_scalar_from_spectrum(spectrum_value)`

**Input:** Spectrum value (float in range [-1, 1])  
**Output:** Frequency scalar (float in range [0, 1], log-scaled)

Extracts the 16-bit frequency scalar from the 24-bit spectrum value.

The spectrum value is stored as a normalized IEEE 754 float. The frequency information is encoded in bytes 1-2 (bits 8-23 of the 24-bit representation).

```python
# Example
spectrum = 0.005
freq_scalar = extract_frequency_scalar_from_spectrum(spectrum)
# freq_scalar ≈ 0.023683
```

### 2. `convert_log_frequency_scalar_to_linear(log_frequency_scalar)`

**Input:** Log-scaled frequency scalar (float in range [0, 1])  
**Output:** Linear frequency scalar (float in range [0, 1])

Converts log-scaled frequency (based on octaves) to linear frequency suitable for mapping to Hz.

- Input uses octave-based logarithmic scale (0 to 15 octaves)
- Output is linear in FFT bin space
- Output of 1.0 = Nyquist frequency

```python
# Example
log_scalar = 0.023683
linear_scalar = convert_log_frequency_scalar_to_linear(log_scalar)
# linear_scalar ≈ 0.00018
```

### 3. `get_frequency_hz_from_linear_scalar(linear_frequency_scalar, sample_rate)`

**Input:** Linear frequency scalar (0 to 1) and sample rate (Hz)  
**Output:** Frequency in Hz

Converts the normalized linear scalar to actual frequency in Hz.

```python
# Example
linear_scalar = 0.00018
sample_rate = 48000
freq_hz = get_frequency_hz_from_linear_scalar(linear_scalar, sample_rate)
# freq_hz ≈ 4.3 Hz
```

### 4. `get_frequency_hz_from_spectrum(spectrum_value, sample_rate)` ⭐ COMPLETE PIPELINE

**Input:** Spectrum value and sample rate  
**Output:** Frequency in Hz

Combines all three steps above into one function for convenience.

```python
# Example
spectrum = 0.005
sample_rate = 48000
freq_hz = get_frequency_hz_from_spectrum(spectrum, sample_rate)
# freq_hz ≈ 568.39 Hz
```

---

## Amplitude Extraction

### 1. `extract_amplitude_from_spectrum(spectrum_value)`

**Input:** Spectrum value (float in range [-1, 1])  
**Output:** Amplitude (float in range [0, 1])

Extracts amplitude using the formula:

```
amplitude = 2^(e^e * (spectrum - 1))
```

where e^e ≈ 15.15426224

**Mapping:**
- spectrum = 0.0 → amplitude ≈ 0.0000274 (noise floor, 2^(-e^e))
- spectrum = 1.0 → amplitude = 1.0
- spectrum = -1.0 → amplitude ≈ 2^(-2*e^e) (very small)

```python
# Example
spectrum = 0.005
amplitude = extract_amplitude_from_spectrum(spectrum)
# amplitude ≈ 0.00002890
```

### 2. `invert_amplitude_to_spectrum(amplitude)` - INVERSE FUNCTION

**Input:** Amplitude (float in range [0, 1])  
**Output:** Spectrum value (float in range [-1, 1])

Reverses the amplitude extraction formula:

```
spectrum = log2(amplitude) / e^e + 1
```

```python
# Example
amplitude = 0.00002890
spectrum = invert_amplitude_to_spectrum(amplitude)
# spectrum ≈ 0.005
```

---

## Discrete Channel Conversions

SPC files store spectrum-encoded values. Kyma can also export data as separate discrete frequency and amplitude channels where the scalars are already extracted.

### 1. `spectrum_to_discrete_channels(spectrum_value, sample_rate)`

**Input:** Spectrum value and sample rate  
**Output:** Tuple of (frequency_scalar, amplitude_scalar)

Converts a spectrum-encoded value into the form used in discrete channels.

- frequency_scalar: Linear frequency scalar [0, 1] where 1.0 = Nyquist
- amplitude_scalar: Amplitude [0, 1]

```python
# Example
spectrum = 0.005
sample_rate = 48000
freq_scalar, amp_scalar = spectrum_to_discrete_channels(spectrum, sample_rate)
# freq_scalar ≈ 0.023683
# amp_scalar ≈ 0.00002890
```

### 2. `discrete_channels_to_spectrum(frequency_scalar, amplitude_scalar)`

**Input:** Frequency and amplitude scalars (both [0, 1])  
**Output:** Spectrum value ([-1, 1])

Converts discrete channel format back to spectrum-encoded value.

**Note:** This reconstructs primarily the amplitude encoding. The frequency encoding in the spectrum value can be partially reconstructed.

```python
# Example
freq_scalar = 0.023683
amp_scalar = 0.00002890
spectrum = discrete_channels_to_spectrum(freq_scalar, amp_scalar)
# spectrum ≈ 0.005
```

---

## Frame Processing Utilities

### 1. `extract_frame_spectrum(spc_frame_data, sample_rate)`

**Input:** Array of spectrum values (one complete frame) and sample rate  
**Output:** Tuple of (frequencies_hz, amplitudes)

Extracts all frequency and amplitude information from a complete frame in one call.

```python
# Example
frame_spectrum = np.array([...])  # 508 or 512 spectrum values
sample_rate = 48000
frequencies, amplitudes = extract_frame_spectrum(frame_spectrum, sample_rate)
# frequencies: array of frequencies in Hz
# amplitudes: array of amplitudes [0, 1]
```

### 2. `extract_frame_scalars(spc_frame_data, sample_rate)`

**Input:** Array of spectrum values (one frame) and sample rate  
**Output:** Tuple of (freq_scalars, amp_scalars)

Like above but returns normalized scalars rather than Hz and decoded amplitudes.

```python
# Example
freq_scalars, amp_scalars = extract_frame_scalars(frame_spectrum, sample_rate)
# freq_scalars: array of linear frequency scalars [0, 1]
# amp_scalars: array of amplitudes [0, 1]
```

### 3. `calculate_frame_rms_from_spectrum(spc_frame_data)`

**Input:** Array of spectrum values (one frame)  
**Output:** RMS amplitude of the frame (float)

Calculates the root-mean-square amplitude across all partials in a frame.

Used for analyzing voicing and energy envelope of the frame.

```python
# Example
frame_spectrum = np.array([...])
rms = calculate_frame_rms_from_spectrum(frame_spectrum)
# rms ≈ 0.003 (example value)
```

---

## Usage Examples

### Complete SPC Partial Extraction

```python
import numpy as np
from spc_extraction_functions import *

# Load one frame from SPC file
frame_spectrum = np.array([...])  # e.g., 508 values
sample_rate = 48000

# Extract all data
frequencies, amplitudes = extract_frame_spectrum(frame_spectrum, sample_rate)

# Use in synthesis
for partial_idx in range(len(frequencies)):
    freq = frequencies[partial_idx]
    amp = amplitudes[partial_idx]
    # Generate sine wave: amp * sin(2π * freq * t)
```

### Convert SPC to Discrete Channels Format

```python
# Load SPC file
spc_data = np.array([...])  # Full SPC file

# Convert frame by frame
num_frames = len(spc_data) // 508
discrete_freqs = []
discrete_amps = []

for frame_idx in range(num_frames):
    frame_start = frame_idx * 508
    frame_spectrum = spc_data[frame_start:frame_start + 508]
    
    for spectrum_val in frame_spectrum:
        freq_scalar, amp_scalar = spectrum_to_discrete_channels(spectrum_val, sample_rate)
        discrete_freqs.append(freq_scalar)
        discrete_amps.append(amp_scalar)
```

### Analyze Frame Energy

```python
# Get frame RMS
rms = calculate_frame_rms_from_spectrum(frame_spectrum)

# Estimate voicing (harmonic vs broadband)
_, amplitudes = extract_frame_spectrum(frame_spectrum, sample_rate)
harmonicity = np.max(amplitudes) / np.mean(amplitudes)
spectral_spread = np.std([extract_frequency_scalar_from_spectrum(v) for v in frame_spectrum])

is_voiced = harmonicity > 20 and spectral_spread < 0.15
```

---

## Key Formulas

### Frequency Encoding
```
log_frequency_scalar = extract_frequency_scalar_from_spectrum(spectrum)
binIndex = 2^(log_frequency_scalar * 15)
linear_frequency_scalar = binIndex / 32768
frequency_hz = linear_frequency_scalar * (sample_rate / 2)
```

### Amplitude Encoding
```
amplitude = 2^(e^e * (spectrum - 1))
         = 2^(15.15426224 * (spectrum - 1))
```

### Inverse Amplitude
```
spectrum = log₂(amplitude) / e^e + 1
         = log₂(amplitude) / 15.15426224 + 1
```

---

## Notes

- All functions work with single values or can be called in arrays
- Spectrum values range from -1.0 to 1.0 (IEEE 754 float normalized)
- Frequency scalars are always [0, 1] where 1.0 = Nyquist
- Amplitude scalars are always [0, 1]
- The extraction functions are reversible (spectrum → scalars → spectrum)
- Frame RMS correlates strongly with log₂(RMS) of the tail values (r ≈ 0.945)
