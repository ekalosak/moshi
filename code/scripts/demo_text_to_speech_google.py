from textwrap import shorten
from google.cloud import texttospeech

text='hello'
voice_name='en-AU-Standard-A'
rate=24000

synthesis_input = texttospeech.SynthesisInput(text=text)
voice=texttospeech.VoiceSelectionParams(language_code='en-AU', name=voice_name)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=rate,
)

request = dict(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config,
)
print(request)

client = texttospeech.TextToSpeechClient()

result = client.synthesize_speech(request=request)
print(shorten(str(result), 128))
