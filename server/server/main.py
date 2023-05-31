from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_chunks(length, num_chunks):
    for i in range(num_chunks):
        yield random_string(length)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_response', {'data': 'Connected to the server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_stream')
def handle_start_stream():
    print('Starting stream')
    for chunk in generate_chunks(10, 3):
        print(chunk)
        emit('stream_data', {'data': chunk})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app)
