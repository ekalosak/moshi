# TODO

## In progress:
- Multiple languages
  - EN, ES, JP out of the box.
  * Use whisper
    - DONE: recognize multiple language
    - TODO: speak multiple languages

## Technical:
- More than a single loop.
  - Refactor the main module and prompt into a main class.
- Backoffs for API rate limiting.
- Print athe ascii characters for the message contents in the response.choices.message.content

## Product
- Record conversations.
- Give vocab stats etc.
- Determine parts of speech where the user has difficulty.
  - Prompt AI to help user learn these things.
- Translate conversation to user's native language when finished.
- Shorter time from finishing utterance to listening for response.
- Embed conversations for knowledgebase search.
