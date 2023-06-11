import asyncio
import os
from unittest import mock

from av import AudioResampler
import pytest
from scipy import signal

from moshi import Message, Role
from server import chat, SAMPLE_RATE, AUDIO_FORMAT, AUDIO_LAYOUT
from server.audio import util

def test_chatter_init():
    chatter = chat.WebRTCChatter()

async def dummy(*a,**k):
    await asyncio.sleep(0.)

def dummy_response(*a,**k):
    return "ast test"

def dummy_speech(frame):
    def _dummy_speech():
        return frame
    return _dummy_speech

@pytest.mark.slow
@pytest.mark.asyncio
@mock.patch('server.chat.WebRTCChatter._WebRTCChatter__transcribe_audio', dummy)
@mock.patch('server.chat.WebRTCChatter._WebRTCChatter__detect_language', dummy)
@mock.patch('server.chat.think.completion_from_assistant', dummy_response)
async def test_chatter_aiortc_components(utterance_audio_track, short_audio_frame, Sink):
    """ Test that the chatter detects the utterance and responds.
    The chatter is initialized here in the order it is in main.py.
    It uses tracks as source and sink, but no network - this just assumes we can at least get PeerConnections and audio
    tracks set up in the WebRTC framework. This test does _not_ test the transcription, synthesis, or chat
    functionality.
    """
    sleep = 20.
    print('initializing chatter and sink (as dummy client); source is utterance_audio_track')
    chatter = chat.WebRTCChatter()
    # chatter.responder._ResponsePlayer__throttle_playback = dummy
    chatter._WebRTCChatter__synth_speech = dummy_speech(short_audio_frame)
    # NOTE patches ^
    chatter.messages.append(Message("user", "usr test"))
    chatter.detector.setTrack(utterance_audio_track)
    sink = Sink(chatter.responder.audio)
    print('chatter and sink initialized, starting them now...')
    await asyncio.gather(chatter.start(), sink.start())
    print(f'chatter and sink started, sleeping {sleep}')
    await asyncio.sleep(sleep) # sec
    print('stopping chatter and sink')
    await asyncio.gather(chatter.stop(), sink.stop())
    print('stopped!')
    utframe = chatter.detector._UtteranceDetector__utterance
    ut_sec = util.get_frame_seconds(utframe)
    assert 8.2 <= ut_sec <= 9., "Utterance detection degraded"  # 8.56 sec nominally
    # Check the messages
    assert chatter.messages[-2] == Message(Role.USR, "usr test")
    assert chatter.messages[-1] == Message(Role.AST, "ast test")
    # Check convolution of utterance with the sink
    res = util.make_resampler()
    _ut = res.resample(utframe)
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
    # utterance_time_length = util.get_frame_seconds(_ut)
    assert 28 < utterance_time_complete_on_sink < 31, "nominally where the end of the utterance might be..?"

@pytest.mark.slow
@pytest.mark.asyncio
@pytest.mark.openai
async def test_chatter_happy_path(utterance_audio_track, Sink):
    """ Check the full integration. """
    chatter = chat.WebRTCChatter()
    chatter.detector.setTrack(utterance_audio_track)
    sink = Sink(chatter.responder.audio)
    await asyncio.gather(chatter.detector.start(), sink.start())
    try:
        done, pending = await asyncio.wait([chatter._WebRTCChatter__main()], timeout=20.)
    finally:
        await asyncio.gather(chatter.detector.stop(), sink.stop())
    if done:
        task = done.pop()
        if task.exception() is not None:
            e = task.exception()
            task.print_stack()
            assert 0, e
    breakpoint()
    a=1
