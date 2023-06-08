import asyncio

from aiortc.mediastreams import MediaStreamError
import av
from av import AudioFrame, AudioFifo
import pytest

from server.audio import responder, util

class Sink:
    """ When provided with a track, the sink will consume from it. """
    def __init__(self, track):
        self.__track = track
        self.__task = None
        self.fifo = AudioFifo()
        self.stream_ended = asyncio.Event()

    async def start(self):
        if self.__task is None:
            self.__task = asyncio.create_task(
                self._mainloop(),
                name="Test Sink class main loop task",
            )

    async def stop(self):
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        self.__task = None

    async def _mainloop(self):
        self.stream_ended.clear()
        while True:
            try:
                frame = await self.__track.recv()
            except MediaStreamError:
                break
            frame.pts = 0
            try:
                self.fifo.write(frame)
            except ValueError as e:
                raise
        self.stream_ended.set()

@pytest.mark.asyncio
async def test_sink(short_audio_track):
    """ Test the Sink test class, ensuring that it collects audio from a track in its fifo and is suitable for usage in
    other tests"""
    sink = Sink(short_audio_track)
    await sink.start()
    await asyncio.wait_for(
        sink.stream_ended.wait(),
        timeout = 2.5,  # substantially longer than the short_wav
    )
    await sink.stop()
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    assert 1. <= frame_time <= 2., "the test.wav is 1.24 sec iirc"

@pytest.mark.asyncio
async def test_responder_track(short_audio_frame):
    """ Write audio and ensure that the audio is played, takes aprox expected amount of time, and that the played audio
    contains the expected audio data. """
    empty_seconds = 1.5  # let the ResponsePlayerStream play <empty_seconds> of silence
    audible_seconds = util.get_frame_seconds(short_audio_frame)
    total_expected_sec = empty_seconds + audible_seconds
    sent = asyncio.Event()
    track = responder.ResponsePlayerStream(sent)
    sink = Sink(track)
    await sink.start()
    await asyncio.sleep(empty_seconds)  # ResponsePlayerStream should write empty_seconds of silence
    track.write_audio(short_audio_frame)
    frame_time = util.get_frame_seconds(short_audio_frame)
    timeout = frame_time + 1.
    await asyncio.wait_for(
        sent.wait(),
        timeout
    )
    await sink.stop()
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    # the extra on top of total_expected_sec accounts for the default 100ms playback throttle plus some compute time
    assert total_expected_sec <= frame_time <= total_expected_sec + .2
    arr = frame.to_ndarray()
    proportion_speech = (arr != 0).sum() / arr.shape[1]
    expected_proportion_speech = audible_seconds / total_expected_sec
    assert expected_proportion_speech - .1 <= proportion_speech <= expected_proportion_speech
