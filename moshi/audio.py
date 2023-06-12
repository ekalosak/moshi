""" This module provide audio processing utilities. """
import io
import os

from aiortc.mediastreams import MediaStreamTrack
import av
from av import AudioFrame, AudioLayout, AudioFormat, AudioResampler, AudioFifo
from loguru import logger
import numpy as np

from moshi import SAMPLE_RATE, AUDIO_FORMAT, AUDIO_LAYOUT

def track_str(track: MediaStreamTrack) -> str:
    """ Tidy repr of a track. """
    return f"{track.readyState}:{track.kind}:{track.id}"

@logger.catch
def make_resampler():
    return AudioResampler(
        format=AUDIO_FORMAT,
        layout=AUDIO_LAYOUT,
        rate=SAMPLE_RATE,
    )

def get_frame_energy(af: AudioFrame) -> float:
    """ Calculate the RMS energy of an audio frame. """
    # TODO dynamic energy detection (i.e. later frames matter more than earlier frames)
    arr = af.to_ndarray()  # produces array with dtype of int16
    # logger.trace(f"arr.shape: {arr.shape}")
    # NOTE int16 is too small for squares of typical signal stregth so int32 is used
    energy = np.sqrt(np.mean(np.square(arr, dtype=np.int32)))
    logger.trace(f"frame energy: {energy:.3f}")
    assert not np.isnan(energy)
    return energy

def get_frame_seconds(af: AudioFrame) -> float:
    """ Calculate the length in seconds of an audio frame. """
    seconds = af.samples / af.rate
    # logger.trace(f"frame seconds: {seconds}")
    return seconds

def get_frame_start_time(frame) -> float:
    """ Get the clock time (relative to the start of the stream) at which the frame should start """
    return frame.pts / frame.rate

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

def write_audio_frame_to_wav(frame: AudioFrame, output_file):
    # Source: https://stackoverflow.com/a/56307655/5298555
    with av.open(output_file, 'w') as container:
        stream = container.add_stream('pcm_s16le')
        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    logger.debug(f"Wrote audio in WAV (pcm_s16le) format to {output_file}")

def load_wav_to_buffer(fp: str) -> AudioFifo:
    with av.open(fp, 'r') as container:
        fifo = AudioFifo()
        for frame in container.decode(audio=0):
            fifo.write(frame)
    return fifo

def load_wav_to_audio_frame(fp: str) -> AudioFrame:
    frame = load_wav_to_buffer(fp).read()
    res = make_resampler()
    return res.resample(frame)[0]

def save_bytes_to_wav_file(filename: str, bytestring: bytes):
    with open(filename, "wb") as f:
        f.write(bytestring)
