import asyncio
import os
from unittest import mock

import pytest
from av import AudioResampler
from scipy import signal

from moshi import (
    AUDIO_FORMAT,
    AUDIO_LAYOUT,
    SAMPLE_RATE,
    Message,
    Model,
    Role,
    audio,
)
from moshi.call.webrtc import WebRTCAdapter

DUMMY_AST_TEXT = "ast test"
DUMMY_USR_TEXT = "usr test"


@pytest.fixture
def adapter():
    return WebRTCAdapter("unstructured")

async def dummy_response(*a, **k):
    return [DUMMY_AST_TEXT]


def dummy_speech(frame):
    async def _dummy_speech(self, *a, **k):
        return frame

    return _dummy_speech


async def dummy_detect_lang(*a, **k) -> str:
    await asyncio.sleep(0.0)
    return "en"


async def dummy_get_voice(*a, **k) -> dict[str, str]:
    await asyncio.sleep(0.0)
    return {"name": "test", "ssml_gender": "test"}


async def dummy_transcribe(*a, **k) -> str:
    await asyncio.sleep(0.0)
    return DUMMY_USR_TEXT


@pytest.mark.asyncio
async def test_adapter_disconnect_bug_15(utterance_audio_track, Sink, adapter):
    """test that, when the user disconnects (i.e. detector gets a MediaStreamError), Moshi fails forward nicely."""
    adapter.detector.setTrack(utterance_audio_track)  # 8s speak, 13s tot
    sink = Sink(adapter.responder.audio)
    print("adapter and sink initialized, starting them now...")
    await asyncio.gather(adapter.start(), sink.start())
    print("adapter and sink started")
    await asyncio.sleep(2)
    print("spoofing 'datachannels connected' signal")
    adapter._WebRTCAdapter__all_connected.set()
    await asyncio.sleep(3)
    print("interrupting detector track")
    utterance_audio_track.stop()
    print("waiting for barf")
    await asyncio.sleep(2)


@pytest.mark.slow
@pytest.mark.asyncio
@mock.patch("moshi.core.lang.detect_language", dummy_detect_lang)
@mock.patch("moshi.core.speech.get_voice", dummy_get_voice)
@mock.patch("moshi.core.speech.transcribe", dummy_transcribe)
@mock.patch("moshi.core.think.completion_from_assistant", dummy_response)
async def test_adapter_aiortc_components(
    utterance_audio_track, short_audio_frame, Sink, adapter,
):
    """Test that the adapter detects the utterance and responds.
    The adapter is initialized here in the order it is in main.py.
    It uses tracks as source and sink, but no network - this just assumes we can at least get PeerConnections and audio
    tracks set up in the WebRTC framework. This test does _not_ test the transcription, synthesis, or chat
    functionality.
    """
    sleep = 20.0
    print(
        "initializing adapter and sink (as dummy client); source is utterance_audio_track"
    )
    adapter.detector.setTrack(utterance_audio_track)
    sink = Sink(adapter.responder.audio)
    # TODO adapter.responder._ResponsePlayer__throttle_playback = dummy
    with mock.patch(
        "moshi.core.WebRTCAdapter._WebRTCAdapter__synth_speech",
        dummy_speech(short_audio_frame),
    ):
        print("adapter and sink initialized, starting them now...")
        await asyncio.gather(adapter.start(), sink.start())
        print("adapter and sink started")
        await asyncio.sleep(2)
        print("spoofing 'datachannels connected' signal")
        adapter._WebRTCAdapter__all_connected.set()
        print(f"sleeping {sleep}")
        await asyncio.sleep(sleep)  # sec
    chat_task = adapter._WebRTCAdapter__task
    print(f"adapter.__task: {chat_task}")
    print("stopping adapter and sink")
    await asyncio.gather(adapter.stop(), sink.stop())
    print("stopped!")
    utframe = adapter.detector._UtteranceDetector__utterance
    ut_sec = audio.get_frame_seconds(utframe)
    assert 8.2 <= ut_sec <= 9.0, "Utterance detection degraded"  # 8.56 sec nominally
    # Check the messages
    assert adapter.messages[-2] == Message(Role.USR, DUMMY_USR_TEXT)
    assert adapter.messages[-1] == Message(Role.AST, DUMMY_AST_TEXT)
    # Check convolution of utterance with the sink
    res = audio.make_resampler()
    _ut = res.resample(utframe)
    assert len(_ut) == 1
    _ut = _ut[0]
    _sk = sink.fifo.read()
    assert _sk.format.name == res.format.name
    assert _sk.layout.name == res.layout.name
    assert _sk.rate == res.rate
    ut = _ut.to_ndarray()
    sk = _sk.to_ndarray()
    print("convolving sk by ut...")
    conv = signal.fftconvolve(sk, ut[::-1], mode="same")
    print(f"convolution done! shape={conv.shape}")
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
    # utterance_time_length = audio.get_frame_seconds(_ut)
    assert (
        33 < utterance_time_complete_on_sink < 34
    ), "nominally where the end of the utterance might be..?"


@pytest.mark.slow
@pytest.mark.asyncio
@pytest.mark.openai
@mock.patch("moshi.utils.think.OPENAI_COMPLETION_MODEL", Model.TEXTADA001)
async def test_adapter_happy_path(short_audio_track, Sink, adapter):
    """Check the full integration."""
    timeout = 30.0
    adapter.detector.setTrack(short_audio_track)
    sink = Sink(adapter.responder.audio)
    await sink.start()
    done, pending = await asyncio.wait(
        [adapter._WebRTCAdapter__main()], timeout=timeout
    )
    await sink.stop()
    if done:
        task = done.pop()
        if task.exception() is not None:
            e = task.exception()
            task.print_stack()
            assert 0, e
    else:
        assert (
            pending
        ), f"Somehow asyncio.wait didn't provide done={done} nor pending={pending}"
        task = pending.pop()
        print(task)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("task cancelled successfully, still a test failure though.")
        raise asyncio.TimeoutError(
            f"The main task={task} timed out after timeout={timeout} seconds"
        )
    assert adapter.messages[-2].role == Role.USR
    assert adapter.messages[-1].role == Role.AST
