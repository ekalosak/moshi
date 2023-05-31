from pprint import pprint
import random
import string
import time
from textwrap import shorten

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from loguru import logger

# import moshi

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

class WebSocketHandler:
    # Custom logger to emit log messages through WebSocket
    def __call__(self, record):
        log_data = {
            'level': record.record['level'].name,
            'message': record.record['message'],
            'time': record.record['time'].isoformat(),
            'name': record.record['name'],
            'function': record.record['function'],
            'line': record.record['line'],
        }
        socketio.emit('log', log_data)

log_handler = WebSocketHandler()
logger.add(log_handler)

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_chunks(length, num_chunks):
    for i in range(num_chunks):
        yield random_string(length)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('server_response', {'data': 'Connected to the server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('start_stream')
def handle_start_stream():
    logger.info('Starting stream')
    for chunk in generate_chunks(10, 10):
        logger.debug(f'prepared chunk: {chunk}')
        logger.info(f'sending chunk: {shorten(chunk, 16)}')
        time.sleep(random.uniform(0., 1.))
        emit('stream_data', {'data': chunk})

@socketio.on('demo_audio_stream')
def handle_demo_audio_stream(audio_data):
    logger.trace('got chunk')
    emit('demo_audio_stream', audio_data)

@app.route('/demo_stream')
def index():
    return render_template('demo_stream.html')

if __name__ == '__main__':
    socketio.run(app)
