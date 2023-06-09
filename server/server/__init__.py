""" This module provides a browser-based user interface for Moshi.
It handles streaming audio from the user's mic to the server and from the server to the user's speakers.
This package is intended to be invoked as a web server from the commandline. It is unusual to, for example, import this
package for use in other Python projects.

In short, this is a Flask app - see https://flask.palletsprojects.com/en/2.3.x/ for more information.
"""
import os

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 48000))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOFORMAT", 'stereo')
