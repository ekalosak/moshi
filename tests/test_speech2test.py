from moshimoshi import speech2text

import speech_recognition as sr

def test_recognize(audio_pair):
    audio, expected_result = audio_pair
