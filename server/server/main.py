import collections

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from loguru import logger
import pyaudio
from speech_recognition import AudioSource
import speech_recognition as sr

from server import util

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

rec = sr.Recognizer()

# NOTE these must match the client's audio formatting parameters
FRAME = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# MAX_SIZE = int(RATE / FRAME * 2)  # 2 seconds worth of time
# audio_deq = collections.deque(maxlen=MAX_SIZE)  # elements are bytestrings of len FRAME
audio_deq = collections.deque()  # mega big max size
recording = False

class WebSocketAudioStream:
    """ This class provides a way to read buffer frames from a websocket bytestream representing audio data.
    This is where buffering may be done in the future
    """
    def __init__(self, deq):
        self.deq = deq

    def read(self, size=FRAME) -> 'Frame':
        assert size == FRAME, f"WebSocketAudioStream only supports reading chunks of size {FRAME}, got: {size}"
        return self.deq.pop()

class WebSocketAudioSource(AudioSource):
    """ This class provides a way to adapt a websocket stream of audio bytes into an AudioSource for speech_recognition. """
    def __init__(self, deq):
        self.format = FORMAT
        self.CHUNK = FRAME  # so named due to speech_recognition.Recognizer requirement
        self.SAMPLE_RATE = RATE
        self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.format)
        self.deq = deq
        self.stream = None

    def __enter__(self):
        """ Set up the stream and return self. """
        self.stream = WebSocketAudioStream(self.deq)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Tear down the stream. """
        self.stream = None

audio_source = WebSocketAudioSource(audio_deq)

@socketio.on('demo_audio_stream')
def handle_audio_data(frame):
    """ Write frames of the audio stream to the WebSocketAudioSource. """
    assert len(frame) == FRAME, f"Got unexpected frame size: {len(frame)}; expected: {FRAME}"
    if recording:
        audio_deq.append_left(frame)

@socketio.on('listen')
def handle_listen_request():
    print('got listen request')
    audio_deq.clear()
    recording = True
    emit('start_recording')
    with audio_source as source:
        audio = rec.listen(source)
    recording = False
    emit('stop_recording')
    transcript = rec.recognize_sphinx(audio)
    emit('transcript', transcript)

@socketio.on('transcript')
def log_transcript(transcript):
    logger.info(f"Got transcript: {transcript}")

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('server_response', {'data': 'Connected to the server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@app.route('/')
def demo_audio_recognition():
    return render_template('demo_audio_recognition.html')

if __name__ == '__main__':
    socketio.run(app)
