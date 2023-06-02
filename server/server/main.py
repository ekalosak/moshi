import io
import collections

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from loguru import logger
import pyaudio
from speech_recognition import AudioSource
import speech_recognition as sr

from server import util

# these must match the client's audio formatting parameters
FRAME = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

rec = sr.Recognizer()
buffer = io.BytesIO()

MAX_BUFFER_SIZE = 1024 * 1024 * 8  # 8MiB

class WebSocketAudioStream:
    """ This class provides a way to read frames from a websocket bytestream representing audio data.
    """
    def __init__(self, buf):
        self.buf = buf
        self.pos = self.buf.tell()

    def read(self, size=FRAME) -> 'Frame':
        # TODO may require a synchronization to handle the race condition between having seek'd to pos and having
        # written new frames: https://chat.openai.com/c/940dc6ea-de06-4610-85ee-9a4ec0fb3b0a
        # also truncating the buffer to keep its size under control
        # TODO Consider abstracting the buffer into this class entirely to control this stuff.
        self.buf.seek(self.pos)
        self.pos += size
        frame = self.buf.read(size)
        return frame

class WebSocketAudioSource(AudioSource):
    """ This class provides a way to adapt a websocket stream of audio bytes into an AudioSource for speech_recognition. """
    def __init__(self, buf):
        self.format = FORMAT
        self.CHUNK = FRAME  # so named due to speech_recognition.Recognizer requirement
        self.SAMPLE_RATE = RATE
        self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.format)
        self.buf = buf
        self.stream = None

    def __enter__(self):
        """ Set up the stream and return self. """
        self.stream = WebSocketAudioStream(self.buf)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Tear down the stream. """
        self.stream = None

audio_source = WebSocketAudioSource(buffer)

@socketio.on('demo_audio_stream')
def handle_audio_data(frame):
    """ Write frames of the audio stream to the WebSocketAudioSource. """
    assert len(frame) == FRAME, f"Got unexpected frame size: {len(frame)}; expected: {FRAME}"
    assert isinstance(frame, bytes), f"Expected bytestring, got: {type(frame)}"
    buf_sz = buffer.getbuffer().nbytes + len(frame)
    if buf_sz > MAX_BUFFER_SIZE:
        logger.info(f"truncating buffer as its size is {buf_sz} bytes.")
        truncated_size = buffer.truncate(buffer.tell())
        buffer.seek(0)
        logger.debug(f"truncated size: {truncated_size}")
    buffer.write(frame)

@socketio.on('listen')
def handle_listen_request():
    logger.debug('got listen request')
    emit('start_recording')
    with audio_source as source:
        audio = rec.listen(source)
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
