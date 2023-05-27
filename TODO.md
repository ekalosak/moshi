# TODO

## In progress:
- [P1] stop clipping the responses
- [P1] speak in the detected language

## Tickets
- [P2] clean assistant responses of the "user: ", "Assistant: " etc. pieces
- [P3] detect the AI responding that it doesn't understand
    - include in the final report, but make sure it doesn't make it into the transcript
- [P3] record conversations en toto; save to disk upon exit
- [P3] generate a "teacher's report"
- [P4] thread the openai calls; add a keepalive debug message
- [P4] print athe ascii characters for the message contents in the response.choices.message.content
- [P4] backoffs for API rate limiting.
    - openai.error.RateLimitError

## Product
- Plugins:
    - Plugin system design in DESIGN.md
    - Create a prompt alteration that injects a text article for discussion (story, news, etc.)
- Curricula:
    - Research and design a theory of curriculum
    - Grammar:
        - simple sentence structure
        - basic prepositions
        - action verbs and adverbs
    - Vocabulary:
        - colors
        - numbers
        - animals
- Determine parts of speech where the user has difficulty.
  - Prompt AI to help user learn these things.
- Translate conversation to user's native language when finished.
- Shorter time from finishing utterance to listening for response.
- Embed conversations for knowledgebase search.
- Rename to "Moshi"

# DONE

## 23.5.3
- [P1] restore `python -m moshimoshi` functionality; quasi-works
- [P1] __eq__ for Language based on lang not region
- [P2] more than a single loop.
- [P3] try `max_tokens` in the `lang.recognize_language`

## 23.5.2

- [P0] Allow usage of text-davinci-003 not just gpt-3.5
  - Replicate by `OPENAI_MODEL=text-davinci-003 pytest tests/test_lang.py`
  - see moshimoshi/think.py; working on abstracting the model-endpoint compatability inside `completion_from_assistant()`
