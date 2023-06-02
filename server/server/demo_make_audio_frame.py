import av
import numpy as np

# Generate a dummy audio frame with random audio data
sample_rate = 44100
frame_size = 1024
num_channels = 2

# Create a numpy array with random audio data
audio_data = np.random.randint(low=-32768, high=32767, size=(frame_size, num_channels), dtype=np.int16).T

# Create the audio frame from the numpy array
audio_frame = av.AudioFrame.from_ndarray(audio_data, format='s16', layout='stereo')
audio_frame.sample_rate = sample_rate

# Print some information about the audio frame
print("Audio Frame Format:", audio_frame.format.name)
print("Audio Frame Layout:", audio_frame.layout.name)
print("Sample Rate:", audio_frame.sample_rate)
print("Number of Samples:", audio_frame.samples)
print("Number of Channels:", audio_frame.layout.channels)

af = audio_frame
breakpoint()
a
