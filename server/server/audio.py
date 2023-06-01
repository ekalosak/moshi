""" This module provides a minimal implementation of the speech_recognition and pyaudio adapter for streaming audio from
the websocket. """
import speech_recognition as sr
from speech_recognition import AudioSource
import pyaudio

class WebSocketAudioSource(AudioSource):
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self, size):
        return self.stream.read(size)

    def get_segment_size(self):
        return self.stream.get_segment_size()

    def get_segment_duration(self):
        return self.stream.get_segment_duration()

rec = sr.Recognizer()
audio_source = None

def get_transcript():
    if audio_source:
        with audio_source as source:
            audio = rec.listen(source)
        return rec.recognize_sphinx(audio)
    else:
        return ""

def handle_audio_stream(audio_data):
    if audio_source:
        audio_source.stream.write(audio_data)

def register_routes(socketio):
    @socketio.on('audio_stream')
    def handle_audio_stream_event():
        global audio_source
        if audio_source is None:
            p = pyaudio.PyAudio()

            def callback(in_data, frame_count, time_info, status):
                data = audio_source.read(frame_count)
                return data, pyaudio.paContinue

            audio_source = WebSocketAudioSource(p.open(format=pyaudio.paInt16,
                                                      channels=1,
                                                      rate=16000,
                                                      input=True,
                                                      frames_per_buffer=1024,
                                                      stream_callback=callback))
            socketio.emit('audio_stream_ready')

    @socketio.on('audio')
    def handle_audio_chunk(audio_chunk):
        handle_audio_stream(audio_chunk)

def register_routes(socketio):
    @socketio.on('audio_stream')
    def handle_audio_stream(audio_data):
        audio_source.append_audio(audio_data)


class WebSocketAudioSource(AudioSource):
    def __init__(self, stream: pyaudio.PyAudio.Stream):
        self.stream = stream

    def write(self, chunk):
        self.stream

def make_pyaudio_stream():
    p = pyaudio.PyAudio()
    def callback(in_data, frame_count, time_info, status):
        data = audio_source.read(frame_count)
        return data, pyaudio.paContinue
    audio_source = WebSocketAudioSource(p.open(format=pyaudio.paInt16,
                                              channels=1,
                                              rate=16000,
                                              input=True,
                                              frames_per_buffer=1024,
                                              stream_callback=callback))
    socketio.emit('audio_stream_ready')

audio_stream = make_pyaudio_stream()
audio_source = WebSocketAudioSource(audio_stream)
