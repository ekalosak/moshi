""" This module provide audio processing utilities. """
import os
import tempfile

import numpy as np
from aiortc.mediastreams import MediaStreamTrack
from av import AudioFifo, AudioFormat, AudioFrame, AudioLayout, AudioResampler
from loguru import logger

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 48000))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", "s16")
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOLAYOUT", "stereo")
logger.info(f"Using sample rate: {SAMPLE_RATE}")
logger.info(f"Using audio format: {AUDIO_FORMAT}")
logger.info(f"Using audio layout: {AUDIO_LAYOUT}")

logger.success("Loaded!")


def track_str(track: MediaStreamTrack) -> str:
    """Tidy repr of a track."""
    return f"{track.readyState}:{track.kind}:{track.id}"


@logger.catch
def make_resampler():
    return AudioResampler(
        format=AUDIO_FORMAT,
        layout=AUDIO_LAYOUT,
        rate=SAMPLE_RATE,
    )


def get_frame_energy(af: AudioFrame) -> float:
    """Calculate the RMS energy of an audio frame."""
    # TODO dynamic energy detection (i.e. later frames matter more than earlier frames)
    arr = af.to_ndarray()  # produces array with dtype of int16
    # logger.trace(f"arr.shape: {arr.shape}")
    # NOTE int16 is too small for squares of typical signal stregth so int32 is used
    energy = np.sqrt(np.mean(np.square(arr, dtype=np.int32)))
    logger.trace(f"frame energy: {energy:.3f}")
    assert not np.isnan(energy)
    return energy


def get_frame_seconds(af: AudioFrame) -> float:
    """Calculate the length in seconds of an audio frame."""
    seconds = af.samples / af.rate
    # logger.trace(f"frame seconds: {seconds}")
    return seconds


def get_frame_start_time(frame) -> float:
    """Get the clock time (relative to the start of the stream) at which the frame should start"""
    return frame.pts / frame.rate


def empty_frame(
    length=128, format=AUDIO_FORMAT, layout=AUDIO_LAYOUT, rate=SAMPLE_RATE, pts=None
) -> AudioFrame:
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

def af2wavbytes(af: AudioFrame) -> bytes:
    """Convert an AudioFrame to a bytestring in WAV format."""
    if af.format.name != AUDIO_FORMAT:
        logger.warning(f"AudioFrame format {af.format.name} != {AUDIO_FORMAT}")
    if af.layout.name != AUDIO_LAYOUT:
        logger.warning(f"AudioFrame layout {af.layout.name} != {AUDIO_LAYOUT}")
    if af.rate != SAMPLE_RATE:
        logger.warning(f"AudioFrame rate {af.rate} != {SAMPLE_RATE}")
    return af.to_ndarray().tobytes()

def wavbytes2af(b: bytes) -> AudioFrame:
    """Convert a bytestring in WAV format to an AudioFrame."""
    af = AudioFrame.from_ndarray(
        np.atleast_2d(np.frombuffer(b, dtype=np.int16)),
        format=AUDIO_FORMAT,
        layout=AUDIO_LAYOUT,
    )
    af.rate = SAMPLE_RATE
    return af