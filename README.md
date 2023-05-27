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

For a development installation, use the `-e` flag:
```sh
mkdir egg && \
    pip install -e .[dev,test]
```
Note that the `setup.cfg` puts the `.egg-info` into the local `./egg` directory; you have to create the `egg` dir first.

## Usage
After setting up, run:
```sh
python -m moshimoshi
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

- `OPENAI_MODEL` default `gpt-3.5-turbo`
- `MOSHI_LANGUAGE_DETECT_COMPLETIONS` default 3; how many completions to use when trying to detect the language.
