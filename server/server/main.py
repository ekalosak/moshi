import random
import string

from flask import Flask, render_template, Response, stream_with_context

app = Flask(__name__)

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_chunks(length, num_chunks):
    for i in range(num_chunks):
        yield random_string(length)

@app.route('/stream', methods=['GET'])
def stream():
    @stream_with_context
    def generate():
        for chunk in generate_chunks(10, 10):
            print(chunk)
            yield chunk

    response = Response(generate(), mimetype='text/event-stream')
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/num")
def random_num():
    return random.sample(range(3), 1)
