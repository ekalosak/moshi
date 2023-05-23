# 🧑💬🤖 moshimoshi
Have a conversation in another language, at your level.

# Usage
After setting up, run:
```sh
python -m moshimoshi
```

## Environment variables

### Required

- `OPENAI_API_KEY`

### Optional

- `MOSHI_LANGUAGE` default `en-US`
- `MOSHI_RECOGNIZER` default `sphinx`

# Development
These instructions are for developers looking to work on this project.

## Setup
Built using pip and pyenv.

### Venv
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

### Pip
```sh
python3.10 -m pip install --upgrade pip
```

### Install system dependencies
```sh
brew install portaudio
```

### Install Python requirements
```sh
pip install -r requirements.txt
```
