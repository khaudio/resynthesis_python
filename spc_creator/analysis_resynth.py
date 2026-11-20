#!/usr/bin/env python3
"""
COMPLETE PIPELINE: Analyze -> Encode -> Resynthesizes
No padding. Direct analysis of original audio.
Amplitude matching to original peak.
"""

import struct
import numpy as np
from scipy import signal
from scipy.io import wavfile
import warnings

warnings.filterwarnings('ignore')

# Constants
EULER_TO_EULER = np.e ** np.e
FFT_SIZE = 2**16
NYQUIST_BIN = FFT_SIZE // 2
OCTAVE_RANGE = np.log2(NYQUIST_BIN)
AMP_EXP_BASE = EULER_TO_EULER

# USER-ADJUSTABLE: Number of partials/harmonics
NUM_PARTIALS = 128

# USER-ADJUSTABLE: Voicing confidence threshold
VOICING_THRESHOLD = 0.3


def load_aiff_audio(filename):
    """Load mono audio from AIFF file."""
    with open(filename, 'rb') as f:
        data = f.read()
    
    ssnd_pos = data.find(b'SSND')
    chunk_size = struct.unpack('>I', data[ssnd_pos+4:ssnd_pos+8])[0]
    offset_field = struct.unpack('>I', data[ssnd_pos+8:ssnd_pos+12])[0]
    
    ssnd_data_start = ssnd_pos + 16 + offset_field
    audio_data_size = chunk_size - 8 - offset_field
    num_samples = audio_data_size // 3
    
    samples = []
    for i in range(num_samples):
        offset = ssnd_data_start + (i * 3)
        b0, b1, b2 = data[offset], data[offset+1], data[offset+2]
        val = (b0 << 16) | (b1 << 8) | b2
        if val >= 0x800000:
            val = val - 0x1000000
        samples.append(val / 0x800000)
    
    return np.array(samples, dtype=np.float64)


def encode_spectrum_value(frequency_hz, amplitude, sample_rate):
    """Encode frequency and amplitude into a 24-bit spectrum value."""
    nyquist = sample_rate / 2.0
    if frequency_hz < 0 or frequency_hz > nyquist:
        frequency_hz = np.clip(frequency_hz, 0, nyquist)
    if amplitude < 0 or amplitude > 1.0:
        amplitude = np.clip(amplitude, 0, 1.0)
    
    # Encode amplitude
    if amplitude <= 0:
        spectrum_value = -1.0
    else:
        spectrum_value = np.log2(amplitude) / AMP_EXP_BASE + 1.0
    
    spectrum_int = int(spectrum_value * 8388608)
    if spectrum_int < 0:
        spectrum_int += 0x1000000
    spectrum_int &= 0xFFFFFF
    
    # Encode frequency into bits 15-0
    linear_scalar = frequency_hz / nyquist
    if linear_scalar <= 0:
        log_scalar = 0
    else:
        binIndex = linear_scalar * NYQUIST_BIN
        log_scalar = np.log2(binIndex) / OCTAVE_RANGE if binIndex >= 1 else 0
    
    freq_int = int(log_scalar * 65536) & 0xFFFF
    spectrum_int = (spectrum_int & 0xFFFF0000) | freq_int
    
    if spectrum_int >= 0x800000:
        spectrum_int -= 0x1000000
    
    return spectrum_int / 8388608.0


def write_aiff_spectrum(filename, spectrum_values, sample_rate):
    """Write spectrum values as AIFF file."""
    num_samples = len(spectrum_values)
    
    # Convert to 24-bit integers
    samples_24bit = []
    for val in spectrum_values:
        spectrum_int = int(val * 8388608)
        if spectrum_int < 0:
            spectrum_int += 0x1000000
        spectrum_int &= 0xFFFFFF
        samples_24bit.append(spectrum_int)
    
    # Build COMM chunk
    num_channels = 1
    bits_per_sample = 24
    comm_chunk = b'COMM'
    comm_chunk += struct.pack('>I', 18)
    comm_chunk += struct.pack('>H', num_channels)
    comm_chunk += struct.pack('>I', num_samples)
    comm_chunk += struct.pack('>H', bits_per_sample)
    comm_chunk += b'\x40\x0e\xac\x44\x00\x00\x00\x00\x00\x00'
    
    # Build SSND chunk
    ssnd_chunk = b'SSND'
    ssnd_data = b''
    for sample in samples_24bit:
        val = sample & 0xFFFFFF
        ssnd_data += bytes([(val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF])
    
    ssnd_chunk += struct.pack('>I', len(ssnd_data) + 8)
    ssnd_chunk += struct.pack('>I', 0)
    ssnd_chunk += struct.pack('>I', 0)
    ssnd_chunk += ssnd_data
    
    # Combine and write
    form_data = comm_chunk + ssnd_chunk
    form_chunk = b'FORM'
    form_chunk += struct.pack('>I', len(form_data) + 4)
    form_chunk += b'AIFF'
    form_chunk += form_data
    
    with open(filename, 'wb') as f:
        f.write(form_chunk)


def estimate_f0_autocorr(audio, sr, frame_start, frame_size=2048, voicing_threshold=None):
    """Estimate F0 using autocorrelation."""
    if voicing_threshold is None:
        voicing_threshold = VOICING_THRESHOLD
    
    end = min(frame_start + frame_size, len(audio))
    if end - frame_start < frame_size // 2:
        return None
    
    frame = audio[frame_start:end]
    if len(frame) < frame_size // 2:
        return None
    
    window = signal.get_window('hann', len(frame))
    frame_windowed = frame * window
    
    autocorr = np.correlate(frame_windowed, frame_windowed, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0]
    
    min_lag = int(sr / 300)
    max_lag = int(sr / 60)
    
    if max_lag >= len(autocorr):
        max_lag = len(autocorr) - 1
    
    search_region = autocorr[min_lag:max_lag]
    if len(search_region) == 0:
        return None
    
    peak_lag = np.argmax(search_region) + min_lag
    
    if peak_lag <= 0 or autocorr[peak_lag] < voicing_threshold:
        return None
    
    return sr / peak_lag


def analyze_and_encode(audio_file, sr=44100, hop_length=128, n_fft=2048, n_harmonics=None):
    """Analyze audio and encode to spectrum values. NO PADDING."""
    
    if n_harmonics is None:
        n_harmonics = NUM_PARTIALS
    
    print(f"Loading audio...", end=" ", flush=True)
    audio = load_aiff_audio(audio_file)
    original_length = len(audio)
    original_peak = np.max(np.abs(audio))
    original_rms = np.sqrt(np.mean(audio ** 2))
    print(f"({original_length:,} samples, peak={original_peak:.6f})")
    
    # Pad input to preserve full length through STFT
    # Use padding that's a multiple of NUM_PARTIALS for clean boundaries
    # 8 frames worth of padding = 8 * hop_length = 1024 samples
    pad_amount = hop_length * 8  # Equivalent to n_fft // 2, but now scales cleanly
    audio = np.concatenate([np.zeros(pad_amount), audio, np.zeros(pad_amount)])
    print(f"Padded input: {len(audio):,} samples ({pad_amount} front + {pad_amount} back, {pad_amount // hop_length} frames)")
    
    # STFT
    print(f"Computing STFT...", end=" ", flush=True)
    window = signal.get_window('hann', n_fft)
    n_frames = (len(audio) - n_fft) // hop_length + 1
    
    stft_mag = np.zeros((n_fft // 2 + 1, n_frames))
    stft_phase = np.zeros((n_fft // 2 + 1, n_frames))
    
    for frame_idx in range(n_frames):
        start = frame_idx * hop_length
        end = start + n_fft
        
        if end > len(audio):
            break
        
        frame = audio[start:end] * window
        fft_result = np.fft.rfft(frame, n=n_fft)
        stft_mag[:, frame_idx] = np.abs(fft_result)
        stft_phase[:, frame_idx] = np.angle(fft_result)
    
    print(f"({n_frames} frames)")
    
    # Analysis
    print(f"Extracting harmonics...", end=" ", flush=True)
    spectrum_values = []
    
    for frame_idx in range(n_frames):
        mag_frame = stft_mag[:, frame_idx]
        phase_frame = stft_phase[:, frame_idx]
        
        # F0 detection
        frame_start = frame_idx * hop_length
        f0 = estimate_f0_autocorr(audio, sr, frame_start, n_fft, voicing_threshold=VOICING_THRESHOLD)
        
        if f0 is None or f0 < 60:
            # UNVOICED: Extract spectral peaks
            mag_smoothed = signal.savgol_filter(mag_frame, window_length=min(11, len(mag_frame)//4*2+1), polyorder=2)
            peaks, props = signal.find_peaks(mag_smoothed, height=np.max(mag_smoothed) * 0.10)
            
            if len(peaks) > 0:
                heights = props['peak_heights']
                sorted_idx = np.argsort(-heights)
                peaks = peaks[sorted_idx[:n_harmonics]]
            else:
                peaks = []
            
            for peak_bin in peaks:
                if peak_bin > 0 and peak_bin < len(mag_frame) - 1:
                    y1 = mag_frame[peak_bin - 1]
                    y2 = mag_frame[peak_bin]
                    y3 = mag_frame[peak_bin + 1]
                    
                    denom = 2*y2 - y1 - y3
                    if abs(denom) > 1e-10:
                        delta = (y3 - y1) / (2 * denom)
                        refined_bin = peak_bin + delta
                    else:
                        refined_bin = float(peak_bin)
                else:
                    refined_bin = float(peak_bin)
                
                freq_hz = refined_bin * sr / n_fft
                amp = mag_frame[peak_bin] / (n_fft / 2) * 2
                amp = np.clip(amp, 0, 1)
                
                spectrum_values.append(encode_spectrum_value(freq_hz, amp, sr))
            
            for _ in range(n_harmonics - len(peaks)):
                spectrum_values.append(encode_spectrum_value(0, 1e-6, sr))
            
            if (frame_idx + 1) % 100 == 0:
                print(f"\n  {frame_idx + 1}/{n_frames}", end=" ", flush=True)
            continue
        
        # VOICED: Extract harmonics at exact n*F0
        for harmonic_num in range(1, n_harmonics + 1):
            expected_freq = f0 * harmonic_num
            
            if expected_freq > sr / 2:
                spectrum_values.append(encode_spectrum_value(0, 1e-6, sr))
                continue
            
            # Find FFT bin
            bin_idx = expected_freq * n_fft / sr
            bin_low = int(np.floor(bin_idx))
            bin_high = int(np.ceil(bin_idx))
            
            if bin_high >= len(mag_frame):
                spectrum_values.append(encode_spectrum_value(0, 1e-6, sr))
                continue
            
            # Interpolate magnitude
            frac = bin_idx - bin_low
            amp = (1 - frac) * mag_frame[bin_low] + frac * mag_frame[bin_high]
            amp = amp / (n_fft / 2) * 2
            amp = np.clip(amp, 0, 1)
            
            spectrum_values.append(encode_spectrum_value(expected_freq, amp, sr))
        
        if (frame_idx + 1) % 100 == 0:
            print(f"\n  {frame_idx + 1}/{n_frames}", end=" ", flush=True)
    
    print()
    return np.array(spectrum_values, dtype=np.float64), original_length, original_peak, original_rms


def resynthesizes(spectrum_values, sr=44100, n_harmonics=None, output_file=None, original_length=None, original_peak=None):
    """Resynthesizes audio from spectrum values."""
    
    if n_harmonics is None:
        n_harmonics = NUM_PARTIALS
    
    print(f"\nResynthesizing...", end=" ", flush=True)
    
    # Oscillator
    class Oscillator:
        def __init__(self, sr, freq, amp):
            self.sr = sr
            self.freq = freq
            self.amp = amp
            self.phase = 0.0
        
        def __call__(self, n_samples):
            if self.freq == 0:
                return np.zeros(n_samples)
            inc = 2 * np.pi * self.freq / self.sr
            samples = self.amp * np.sin(self.phase + np.arange(n_samples) * inc)
            self.phase = (self.phase + inc * n_samples) % (2 * np.pi)
            return samples
    
    # Decode spectrum values and resynthesizes
    output = []
    osc_bank = [Oscillator(sr, 0, 0) for _ in range(n_harmonics)]
    
    for idx, spectrum_val in enumerate(spectrum_values):
        # Extract frequency
        spectrum_int = int(spectrum_val * 8388608)
        if spectrum_int < 0:
            spectrum_int += 0x1000000
        spectrum_int &= 0xFFFFFF
        
        byte12 = spectrum_int & 0xFFFF
        freq_scalar = byte12 / 65536.0
        binIndex = 2 ** (freq_scalar * OCTAVE_RANGE)
        linear = binIndex / NYQUIST_BIN
        freq_hz = linear * (sr * 0.5)
        
        # Extract amplitude
        amp = 2.0 ** (AMP_EXP_BASE * (spectrum_val - 1.0))
        
        # Update oscillator
        partial_idx = idx % n_harmonics
        osc_bank[partial_idx].freq = freq_hz
        osc_bank[partial_idx].amp = amp
        
        # Generate sample
        sample = sum(osc(1)[0] for osc in osc_bank)
        output.append(sample)
        
        if (idx + 1) % 10000 == 0:
            print(f"\n  {idx + 1}/{len(spectrum_values)}", end=" ", flush=True)
    
    print()
    
    output = np.array(output, dtype=np.float64)
    
    # TRIM OUTPUT to original length (remove extra spectrum values from padding)
    if original_length is not None:
        extra_samples = len(output) - original_length
        if extra_samples > 0:
            # Trim evenly from both front and back to keep signal centered
            trim_front = extra_samples // 2
            trim_back = extra_samples - trim_front
            output = output[trim_front:-trim_back] if trim_back > 0 else output[trim_front:]
    
    # Match original amplitude
    if original_peak is not None and original_peak > 0:
        peak_output = np.max(np.abs(output))
        if peak_output > 0:
            output = output * (original_peak / peak_output)
    
    if output_file:
        wavfile.write(output_file, sr, (output * 32767).astype(np.int16))
    
    return output


if __name__ == '__main__':
    print("="*100)
    print("COMPLETE PIPELINE: Analyze -> Encode -> Resynthesizes")
    print("="*100)
    print(f"\nParameters:")
    print(f"  NUM_PARTIALS: {NUM_PARTIALS} (change at top of file to use different partial counts)")
    print(f"  VOICING_THRESHOLD: {VOICING_THRESHOLD}")
    print(f"  UNVOICED_PEAK_THRESHOLD: 10% (0.10)")
    
    # Step 1: Analyze
    spectrum_values, orig_len, orig_peak, _ = analyze_and_encode(
        '/mnt/user-data/uploads/carla_iam_original_audio.aif',
        sr=44100,
        hop_length=128,
        n_fft=2048,
        n_harmonics=NUM_PARTIALS
    )
    
    print(f"\nEncoded {len(spectrum_values):,} spectrum values")
    
    # Step 2: Write SPC file
    print(f"\nWriting SPC file...", end=" ", flush=True)
    write_aiff_spectrum(
        '/mnt/user-data/outputs/carla_iam_analyzed.spc',
        spectrum_values,
        sample_rate=44100
    )
    print(f"done")
    print(f"  /mnt/user-data/outputs/carla_iam_analyzed.spc")
    
    # Step 3: Resynthesizes
    audio_out = resynthesizes(
        spectrum_values,
        sr=44100,
        n_harmonics=NUM_PARTIALS,
        output_file='/mnt/user-data/outputs/carla_iam_from_my_analysis.wav',
        original_length=orig_len,
        original_peak=orig_peak
    )
    
    print(f"\n✓ /mnt/user-data/outputs/carla_iam_from_my_analysis.wav")
    print(f"  Duration: {len(audio_out) / 44100:.3f} seconds")
    print(f"  Peak amplitude: {np.max(np.abs(audio_out)):.6f}")
