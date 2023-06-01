import random
import string

from loguru import logger

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_chunks(length, num_chunks):
    for i in range(num_chunks):
        yield random_string(length)

class WebSocketHandler:
    # Custom logger to emit log messages through WebSocket
    def __init__(self, socketio):
        self.socketio = socketio

    def __call__(self, record):
        log_data = {
            'level': record.record['level'].name,
            'message': record.record['message'],
            'time': record.record['time'].isoformat(),
            'name': record.record['name'],
            'function': record.record['function'],
            'line': record.record['line'],
        }
        self.socketio.emit('log', log_data)

def handle_demo_audio_stream(audio_data):
    logger.trace('got chunk')
    emit('demo_audio_stream', audio_data)

def handle_start_stream():
    logger.info('Starting stream')
    for chunk in generate_chunks(10, 10):
        logger.debug(f'prepared chunk: {chunk}')
        logger.info(f'sending chunk: {shorten(chunk, 16)}')
        time.sleep(random.uniform(0., 1.))
        emit('stream_data', {'data': chunk})

def demo_stream_mic():
    return render_template('demo_stream_mic.html')

def register_routes(socketio, app):
    log_handler = WebSocketHandler(socketio)
    logger.add(log_handler)
    app.route('/demo_stream')(demo_stream_mic)
    socketio.on('start_stream')(handle_start_stream)
    socketio.on('demo_audio_stream')(handle_demo_audio_stream)
