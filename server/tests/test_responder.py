import asyncio
from av import AudioFifo
import pytest

from server.audio import responder, util

class Sink:
    """ When provided with a track, the sink will consume from it. """
    def __init__(self, track):
        self.__track = track
        self.fifo = AudioFifo()
        self.stream_ended = asyncio.Event()

    async def start(self):
        if self.__task is None:
            self.__task = await asyncio.create_task(self._mainloop)

    async def stop(self):
        await self.__task.cancel()
        self.__task = None

    async def _mainloop(self):
        while True:
            try:
                frame = await self.track.recv()
            except MediaStreamError:
                break
            self.fifo.write(frame)
        self.stream_ended.notify()

@pytest.mark.asyncio
async def test_sink(short_audio_track):
    sink = Sink(short_audio_track)
    await sink.start()
    await asyncio.wait_for(
        sink.stream_ended.wait(),
        timeout = 5.,  # substantially longer than the short_wav
    )
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    print(frame_time)
    breakpoint()
    a=1

@pytest.mark.asyncio
async def test_responder_track(short_audio_frame):
    """ Write audio and ensure that the audio is played, takes aprox expected amount of time, and that the played audio
    contains the expected audio data. """
    fifo = AudioFifo()
    sent = asyncio.Event()
    track = responder.ResponsePlayerStream(sent)
    sink = Sink(track)
    sink_task = await asyncio.create_task(sink.start(), "Test sink audio task: test_responder_track")
    track.write_audio(short_audio_frame)
    frame_time = util.get_frame_seconds(short_audio_frame)
    timeout = frame_time + 1.
    print(f"frame_time = {frame_time}, timeout = {timeout}")
    await asyncio.wait_for(sent.wait(), timeout)
    await sink.stop()
