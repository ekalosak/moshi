# 23.6.3  Tue Jun 13 13:50:34 EDT 2023
Major refactor, subsuming the CLI into the web server; no more CLI, only web now.
TTS and language det using Google Cloud, see runbook for how to setup cloud services.

# Mixed CLI <> server version

## 23.6.0
WebRTCChatter appears working in smoke-tests (detecting utterance from track, replaying back, handling tracks)

## 23.5.1
Tried a ton of garbage with sockets
Eventually got WebRTC working; initial implementation of utterance detection from audio track on serverside.

## 23.5.0
Basic implementation of text streaming from server to client using websockets.
Logging streamed to frontend.

# CLI version

## 25.6.0
- [P2] Rename to "moshi"
- Move TTS from pyttsx3 or pyttsx4 -> texttospeech.googleapis.com
- Move language detection -> translate.googleapis.con
* Subsumed into server

## 23.5.3
- full MVP implemented - the core chat loop "just works".
- restored `python -m moshimoshi` functionality; mostly works as expected modulo bugs.
- [BUG-01] sometimes response (using davinci-003) was a translation; fixed w/ prompt eng.
- [FEAT-01] speak in the detected language;
- __eq__ for Language based on lang not region so `en_US == en_GB == en-scotland` now.
- using `max_tokens = 16` in the `lang.recognize_language`; that works;
- keyboard interrupt quits gracefully;

## 23.5.2
- Major refactor from POC to an architecture appropriate for the POV.
- Introducing Chatter class, object oriented to set up for multi-utterance conversation.
- Decomposed the singular chat completion into two.
  - before, completion and language detection all-in-one
  - after, they're separate api calls
- Use system/user/assistant call structure rather than single monolith prompt.
  - more details on https://platform.openai.com/docs/guides/chat/introduction
- Added tests.
- All chat completion and regular completion models supported (gpt-3.5 and text-x-00y).
- Main functionality still broken, but enough of the refactor and new support is added to make it worth calling this a
  version.

## 23.5.1
- POC implementation of multi-language detection and response.
- Uses whisper-api for stt
- Very buggy language detection.

## 23.5.0
- Hello world implementation - it can listen and respond to a single sentence of English.
- Uses sphinx for stt.
- Only works in English.
