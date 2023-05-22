""" This module abstracts specific speech2text implementations for use in the ChitChat app. """
import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

print("Sphinx thinks you said " + r.recognize_sphinx(audio))
