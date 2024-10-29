import numpy as np
from scipy.io import wavfile
from scipy.fft import rfft, rfftfreq

# Load .wav file
sample_rate, data = wavfile.read(
    "/Users/buweichen/Downloads/Life's Incredible Again.wav"
)

# If stereo, take just one channel (mono conversion)
if len(data.shape) == 2:
    data = data[:, 0]

# Define the window size and step size for FFT analysis
window_size = 2048  # Adjust window size for resolution
step_size = 512  # Step size to move the window (overlap)
tempo = 4  # Example tempo

# Notes and corresponding frequencies (same as your PWM example)
tones = {
    "c": 262,
    "d": 294,
    "e": 330,
    "f": 349,
    "g": 392,
    "a": 440,
    "b": 494,
    "C": 523,
    " ": 0,
}


# Function to map frequency to nearest note
def freq_to_note(freq):
    min_diff = float("inf")
    closest_note = " "
    for note, tone_freq in tones.items():
        diff = abs(freq - tone_freq)
        if diff < min_diff:
            min_diff = diff
            closest_note = note
    return closest_note


# Arrays to hold the melody and rhythm
melody = []
rhythm = []

# Process each window using FFT
for start in range(0, len(data) - window_size, step_size):
    window = data[start : start + window_size]

    # Apply FFT to the window
    fft_result = rfft(window)
    freqs = rfftfreq(window_size, 1 / sample_rate)

    # Find the peak frequency in the window
    peak_freq = freqs[np.argmax(np.abs(fft_result))]

    # Map the peak frequency to the closest note
    note = freq_to_note(peak_freq)

    # Estimate duration based on the window size
    note_duration = window_size / sample_rate

    # Store the note and its duration (scaled to match rhythm values)
    melody.append(note)
    rhythm.append(int(tempo / note_duration))  # Scaling rhythm

# Print the melody and rhythm arrays
print("Melody: ", "".join(melody))
print("Rhythm: ", rhythm)
