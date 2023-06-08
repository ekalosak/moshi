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
            print('no sink task, starting one')
            self.__task = asyncio.create_task(
                self._mainloop(),
                name="Test Sink class main loop task",
            )
            print(f'sink task: {self.__task}')

    async def stop(self):
        await self.__task.cancel()
        self.__task = None

    async def _mainloop(self):
        print('starting sink _mainloop')
        while True:
            try:
                frame = await self.__track.recv()
            except MediaStreamError:
                break
            self.fifo.write(frame)
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
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    assert 1. <= frame_time <= 2., "the test.wav is 1.24 sec iirc"

@pytest.mark.asyncio
async def test_responder_track(short_audio_frame):
    """ Write audio and ensure that the audio is played, takes aprox expected amount of time, and that the played audio
    contains the expected audio data. """
    fifo = AudioFifo()
    sent = asyncio.Event()
    track = responder.ResponsePlayerStream(sent)
    sink = Sink(track)
    print(f"Created Sink: {sink}")
    await sink.start()
    print(f"Started sink")
    track.write_audio(short_audio_frame)
    print("Wrote audio to track")
    frame_time = util.get_frame_seconds(short_audio_frame)
    timeout = frame_time + 1.
    print(f"frame_time = {frame_time}, timeout = {timeout}")
    await asyncio.wait_for(
        sent.wait(),
        timeout
    )
    await sink.stop()
    breakpoint()
    a
