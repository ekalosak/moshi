# TODO

## In progress:
- [P1] restore `python -m moshimoshi` functionality

## Technical:
- [P2] more than a single loop.
- [P3] Backoffs for API rate limiting.
    - openai.error.RateLimitError
- [P3] try `max_tokens` in the `lang.recognize_language`
- [P4] print athe ascii characters for the message contents in the response.choices.message.content

## Product
- Record conversations.
- Give vocab stats etc.
- Determine parts of speech where the user has difficulty.
  - Prompt AI to help user learn these things.
- Translate conversation to user's native language when finished.
- Shorter time from finishing utterance to listening for response.
- Embed conversations for knowledgebase search.
- Rename to "Moshi"

# DONE

## 23.5.3
- [P1] __eq__ for Language based on lang not region

## 23.5.2

- [P0] Allow usage of text-davinci-003 not just gpt-3.5
  - Replicate by `OPENAI_MODEL=text-davinci-003 pytest tests/test_lang.py`
  - see moshimoshi/think.py; working on abstracting the model-endpoint compatability inside `completion_from_assistant()`
