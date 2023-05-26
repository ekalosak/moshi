# TODO

## In progress:

## Technical:
- [P0] Allow usage of text-davinci-003 not just gpt-3.5
  - Replicate by `OPENAI_MODEL=text-davinci-003 pytest tests/test_lang`
- [P1] restore `python -m moshimoshi` functionality
- [P2] more than a single loop.
- [P3] Backoffs for API rate limiting.
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
