# 🧑💬🤖 moshimoshi
Have a conversation in another language, at your level.

# Development

## Setup

Start pyenv:
```sh
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Make venv:
```sh
pyenv virtualenv 3.10-dev mm310 && \
  pyenv activate mm310
```

Update pip:
```sh
python3.10 -m pip install --upgrade pip
```

Install system dependencies:
```sh
brew install portaudio
```

Install Python requirements:
```sh
pip install .
```
This uses the `pyproject.toml`'s specified dependencies.

## Usage
After setting up, run:
```sh
python -m moshimoshi
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

- `MOSHI_DEBUG` default not set;
  - When set to anything, expect the developer experience.
- `MOSHI_RECOGNIZER` default `whisper-api`
  - Allowed values: `whisper-api`, `sphinx`
- `MOSHI_LANGUAGE` default not set
  - Required when using `sphinx` recognizer
  - Not required when using `whisper-api` recognizer
  - Allowed values: `en-US`

The app should quit at startup with an informative error if it's misconfigured.
