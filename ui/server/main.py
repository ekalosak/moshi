import random

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/num")
def random_num():
    return random.sample(range(3), 1)
