""" This module provides some utility functions. """
import av.audio.frame as av_frame
import av.audio.format as av_format
import pyaudio
# import numpy as np
from loguru import logger

# NOTE likely to delete all the pyaudio stuff because

def pyav_audioframe_to_bytes(af: av_frame.AudioFrame) -> bytes:
    """ Convert an AudioFrame to the bytes representing it.
    Note that the conversion is performed with the frame's own format; if you want a specific format, use a resampler to
    change the frame's format before passing to this function.
    Bytes are produced in 'C' order; little endian;
    Must be mono.
    Source:
        - Little endian produced by speech_recognition:
          https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py#L311
    """
    logger.debug(f"AudioFrame format: {af.format")
    ar = af.to_numpy()  # TODO order, dtype
    bt = ar.tobytes()
    return bt

def pyav_to_pyaudio_format(pyav_format: av_format.AudioFormat) -> int:
    """
    Convert PyAV AudioFormat to PyAudio audio format.

    Args:
        pyav_format (AudioFormat): PyAV audio format.

    Returns:
        int: PyAudio audio format.

    Raises:
        ValueError: If the PyAV format is unsupported.
    """
    if pyav_format == av_format.AudioFormat.PCM_S16LE:
        return pyaudio.paInt16
    elif pyav_format == av_format.AudioFormat.PCM_S16BE:
        return pyaudio.paInt16  # Same as PyAV's S16LE, just different endianness
    elif pyav_format == av_format.AudioFormat.PCM_F32LE:
        return pyaudio.paFloat32
    # Add more mappings as needed for other PyAV formats
    else:
        raise ValueError(f"Unsupported PyAV format: {pyav_format}")

def pyaudio_to_pyav_format(pyaudio_format: int) -> av_format.AudioFormat:
    """
    Convert PyAudio audio format to PyAV AudioFormat.

    Args:
        pyaudio_format (int): PyAudio audio format.

    Returns:
        AudioFormat: PyAV audio format.

    Raises:
        ValueError: If the PyAudio format is unsupported.
    """
    if pyaudio_format == pyaudio.paInt16:
        return av_format.AudioFormat.PCM_S16LE
    elif pyaudio_format == pyaudio.paFloat32:
        return av_format.AudioFormat.PCM_F32LE
    else:
        raise ValueError(f"Unsupported PyAudio format: {pyaudio_format}")
