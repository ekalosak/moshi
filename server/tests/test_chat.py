import asyncio

import pytest

from server import chat

def test_chatter_init():
    chatter = chat.WebRTCChatter()

@pytest.mark.slow
@pytest.mark.asyncio
async def test_chatter_happy_path(utterance_audio_track, Sink):
    """ Test that the chatter detects the utterance and responds. """
    # TODO when WebRTCChatter._main starts using openai, monkeypatch those out
    sleep = 15.   # utterance time (12 sec total w/ silence iirc)+ plenty of silence
    print('initializing chatter and sink (as dummy client); source is utterance_audio_track')
    chatter = chat.WebRTCChatter()
    chatter.detector.setTrack(utterance_audio_track)
    sink = Sink(chatter.responder.audio)
    print('chatter and sink initialized, starting them now...')
    await asyncio.gather(chatter.start(), sink.start())
    print(f'chatter and sink started, sleeping {sleep}')
    await asyncio.sleep(sleep) # sec
    await asyncio.gather(chatter.stop(), sink.stop())
    assert 0, "check the contents of sink are what we expect"
