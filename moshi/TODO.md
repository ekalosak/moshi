# TODO

## In progress:
- [P2] clean assistant responses of the "user: ", "Assistant: " etc. pieces

## Tickets
- [P1] stop clipping the responses; it appears that `max_tokens` is being used or something.
- [P2] Rename to "moshi"
- [P3] detect the AI responding that it doesn't understand
    - include in the final report, but make sure it doesn't make it into the transcript
- [P3] record conversations en toto; save to disk upon exit
- [P3] generate a "teacher's report"
- [P3] Interrupt system
    - saying "quit quit quit" quits;
    - saying "help help help" prints the help text;
    - non-quitting messages should pause after responding and ask user to press space to continue;
- [P3] saying "I don't understand" or similar should cause the model to provide a translation
- [P4] prefer female language in `_get_voice_for_language`
- [P4] thread the openai calls; add a keepalive debug message
- [P4] backoffs for API rate limiting.
    - openai.error.RateLimitError

## Bugs
- Sometimes chat response is completely empty
- Sometimes tts hangs for a long time after utterance
- Seeing "Got finish reason: True" as a warning in logs
    - `moshimoshi.think:_chat_completion:102`
- Sometimes responses can be very repetative; I suspect I should up the frequency penalty or etc.
- Sometimes responses contain special characters like `[`;
    - on their own this is annoying and they should be cleaned
    - in the long term, a response like `[Nombre]` is an opportunity to have an orthogonal system select and record
      attributes.

## Product
- Plugins:
    - Plugin system design in DESIGN.md
    - Create a prompt alteration that injects a text article for discussion (story, news, etc.)
- Curricula:
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

## Backlog
- [P4] print athe ascii characters for the message contents in the response.choices.message.content

# DONE
Move this section to the CHANGELOG.md when you're done.
