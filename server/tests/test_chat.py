import asyncio
import os

from av import AudioResampler
import pytest
from scipy import signal

from server import chat
from server.audio import util

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 44100))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOFORMAT", 'mono')

def test_chatter_init():
    chatter = chat.WebRTCChatter()

@pytest.mark.slow
@pytest.mark.asyncio
async def test_chatter_happy_path(utterance_audio_track, Sink):
    """ Test that the chatter detects the utterance and responds.
    The chatter is initialized here in the order it is in main.py.
    It uses tracks as source and sink, but no network - this just assumes we can at least get PeerConnections and audio
    tracks set up in the WebRTC framework.
    """
    # TODO when WebRTCChatter._main starts using openai, monkeypatch those out
    sleep = 25.  # 15. for the 12. of the utterance detection + overhead; 10. for the 8. of playback + overhead;
    print('initializing chatter and sink (as dummy client); source is utterance_audio_track')
    chatter = chat.WebRTCChatter()
    chatter.detector.setTrack(utterance_audio_track)
    sink = Sink(chatter.responder.audio)
    print('chatter and sink initialized, starting them now...')
    await asyncio.gather(chatter.start(), sink.start())
    print(f'chatter and sink started, sleeping {sleep}')
    await asyncio.sleep(sleep) # sec
    await asyncio.gather(chatter.stop(), sink.stop())
    ut = chatter.detector._UtteranceDetector__utterance
    ut_sec = util.get_frame_seconds(ut)
    assert 7.75 <= ut_sec <= 8.25, "Utterance detection degraded"  # 8.06 sec nominally
    # Check convolution of utterance with the sink
    res = AudioResampler(
        layout=AUDIO_LAYOUT,
        format=AUDIO_FORMAT,
        rate=SAMPLE_RATE,
    )
    _ut = res.resample(ut)
    assert len(_ut) == 1
    _ut = _ut[0]
    _sk = sink.fifo.read()
    assert _sk.format.name == res.format.name
    assert _sk.layout.name == res.layout.name
    assert _sk.rate == res.rate
    ut = _ut.to_ndarray()
    sk = _sk.to_ndarray()
    print('convolving sk by ut...')
    conv = signal.fftconvolve(sk, ut[::-1], mode='same')
    print(f'convolution done! shape={conv.shape}')
    # # diagnostic plotting
    # import matplotlib
    # matplotlib.use('agg')
    # import matplotlib.pyplot as plt
    import numpy as np
    # print('plotting...')
    xs = np.arange(conv.shape[1]) / _sk.rate
    # plt.scatter(xs, conv)
    # print('plotted!')
    # plt.savefig('conv.png')
    utterance_time_complete_on_sink = xs[conv.argmax()]
    utterance_time_length = util.get_frame_seconds(_ut)
    assert utterance_time_complete_on_sink > 2. * utterance_time_length - 1.
    assert utterance_time_complete_on_sink < 2. * utterance_time_length + 1.
