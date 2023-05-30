# moshi
The `moshi` project provides the core functionality for the [Moshi app](../README.md).

# Development

## Development docs
Project status, design, and ticketing system are in these docs:
- `TODO.md` has the most concrete tasks, from statements about product features to concrete technical tickets.
- `NOTES.md` has developer notes regarding technical decisions, particularly icky bugs, etc.

## Usage
After setting up, run:
```sh
LOGURU_LEVEL=INFO OPENAI_MODEL="text-davinci-003" python -m moshi
```

## Tests
```bash
pytest -v -m 'not speak and not openai'
```

## Docs
```
python -m pydoc -b
```

# Operations

## Environment variables

### Required

- `OPENAI_API_KEY`

### Optional

- `OPENAI_MODEL` default `gpt-3.5-turbo`; `text-davinci-003` is also pretty good and has much higher rate limits.
- `MOSHI_LANGUAGE_DETECT_COMPLETIONS` default `3`; how many completions to use when trying to detect the language.
- `MOSHI_MAX_LOOPS` default `0`; max number of AI responses to make in a conversation before quitting.
