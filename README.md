# 🧑💬🤖 moshi
Moshi is a spoken language tutor.

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
pip install moshi
```
This uses the `pyproject.toml`'s specified dependencies.

For a development installation, use the `-e` flag:
```sh
mkdir build && \
    pip install -e moshi[dev,test]
```
Note that the `setup.cfg` puts the `.egg-info` into the local `./build` directory; you MUST create the `build` dir first.

## Docs
```
(cd moshi/ && python -m pydoc -b)
```

# Testing
`pip install moshi[test]` and `pytest -m 'not openai and not gcloud and not slow'`

# Usage
```bash
python moshi/main.py
```
