""" This module provide audio processing utilities. """
from aiortc.mediastreams import MediaStreamTrack
from av import AudioFrame
from loguru import logger
import numpy as np

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
