# 23.5.2 WIP
Major refactor from POC to an architecture appropriate for the POV.
  - object oriented
  - use openai messages structure
Decomposed the singular chat completion into two
  - before, completion and language detection all-in-one
  - after, they're separate api calls

# 23.5.1
POC implementation of multi-language detection and response.
Uses whisper-api for stt
Very buggy language detection.

# 23.5.0
Hello world implementation - it can listen and respond to a single sentence of English.
Uses sphinx for stt.
Only works in English.
