import av
from av import AudioFrame
import pytest

from server import audio

def write_frame(frame: AudioFrame) -> str:
    fn = 'test_utterance.wav'
    container = av.open(fn, 'w')
    try:
        stream = container.add_stream('pcm_s16le', layout='mono')
        stream.rate = 44100
        container.mux(stream.encode(frame))
    finally:
        container.close()
    return fn


@pytest.mark.asyncio
@pytest.mark.slow
async def test_utterance_detector(utterance_audio_track):
    """ Test that the UtteranceDetector can detect an utterance of speech in an audio track containing speech. """
    ud = audio.UtteranceDetector()
    print('created UtteranceDetector')
    ud.setTrack(utterance_audio_track)
    print('set track, starting...')
    await ud.start()
    print('started! getting_utterance...')
    utterance = await ud.get_utterance()
    print('got_utterance! stopping...')
    await ud.stop()
    print('stopped!')
    # fn = write_frame(utterance)
    # print(f"wrote detected utterance to: {fn}")
    assert isinstance(utterance, AudioFrame)
    utterance_time = audio.get_frame_seconds(utterance)
    assert 8. <= utterance_time <= 9., f"{str(utterance_audio_track)} is nominally 8.56 seconds of speech"
