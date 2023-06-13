# 🧑💬🤖 moshi
Moshi is a spoken language tutor.

# Development

## Setup

Install system dependencies:
```sh
brew install portaudio
```

Setup virtualenv and install project & its Python dependencies:
```bash
eval "$(pyenv init -)" && \
    eval "$(pyenv virtualenv-init -)" && \
    pyenv virtualenv 3.10-dev mm310 && \
    pyenv activate mm310 && \
    python3.10 -m pip install --upgrade pip && \
    pip install -e .
```

For a development installation, use the `-e` flag:
```sh
mkdir build && \
    pip install -e .[dev,test]
```
Note that the `setup.cfg` puts the `.egg-info` into the local `./build` directory; you MUST create the `build` dir first.

## Docs
```
(cd moshi/ && python -m pydoc -b)
```

# Testing
Make sure you have the test dependencies installed:
```bash
pip install -e .[test]
```

Test using pytest:
```bash
pytest -m 'not openai and not gcloud and not slow'
```

# Usage

To start the web server:
```bash
python moshi/main.py
```
