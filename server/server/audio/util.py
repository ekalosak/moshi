""" This module provide audio processing utilities. """
import os

from aiortc.mediastreams import MediaStreamTrack
from av import AudioFrame, AudioLayout, AudioFormat
from loguru import logger
import numpy as np

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 44100))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOFORMAT", 'mono')

def _track_str(track: MediaStreamTrack) -> str:
    """ Tidy repr of a track. """
    return f"{track.readyState}:{track.kind}:{track.id}"

def get_frame_energy(af: AudioFrame) -> float:
    """ Calculate the RMS energy of an audio frame. """
    # TODO dynamic energy detection (i.e. later frames matter more than earlier frames)
    arr = af.to_ndarray()  # produces array with dtype of int16
    logger.trace(f"arr.shape: {arr.shape}")
    # int16 is too small for squares of typical signal stregth so int32 is used
    energy = np.sqrt(np.mean(np.square(arr, dtype=np.int32)))
    logger.trace(f"frame energy: {energy}")
    assert not np.isnan(energy)
    return energy

def get_frame_seconds(af: AudioFrame) -> float:
    """ Calculate the length in seconds of an audio frame. """
    seconds = af.samples / af.rate
    logger.trace(f"frame seconds: {seconds}")
    return seconds

def get_frame_start_time(frame) -> float:
    """ Get the clock time (relative to the start of the stream) at which the frame should start """
    return frame.pts * frame.samples / frame.rate

def empty_frame(length=128, format=AUDIO_FORMAT, layout=AUDIO_LAYOUT, rate=SAMPLE_RATE, pts=None) -> AudioFrame:
    fmt = AudioFormat(format)
    lay = AudioLayout(layout)
    size = (len(lay.channels), length)
    samples = np.zeros(size, dtype=np.int16)
    if not fmt.is_planar:
        samples = samples.reshape(1, -1)
    frame = AudioFrame.from_ndarray(samples, format=format, layout=layout)
    frame.rate = rate
    frame.pts = pts
    return frame

def ensure_size(af: AudioFrame, size: int) -> AudioFrame:
    """ Add silence to frames that are too short to make sure they're length == size. """
    raise NotImplementedError
