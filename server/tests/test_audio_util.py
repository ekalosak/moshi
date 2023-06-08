from server.audio import util

def test_ensure_size(short_audio_frame):
    frame = ensure_size(short_audio_frame, short_audio_frame.samples * 2)
    assert frame.samples == short_audio_frame.samples * 2
