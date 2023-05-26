# 23.5.2 WIP
Major refactor from POC to an architecture appropriate for the POV.
Introducing Chatter class, object oriented to set up for multi-utterance conversation.
Decomposed the singular chat completion into two.
  - before, completion and language detection all-in-one
  - after, they're separate api calls
Use system/user/assistant call structure rather than single monolith prompt.
  - more details on https://platform.openai.com/docs/guides/chat/introduction
Added tests.

# 23.5.1
POC implementation of multi-language detection and response.
Uses whisper-api for stt
Very buggy language detection.

# 23.5.0
Hello world implementation - it can listen and respond to a single sentence of English.
Uses sphinx for stt.
Only works in English.
