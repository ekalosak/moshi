# chitchat
Have a conversation in another language, at your level.

# Development
These instructions are for developers looking to work on this project.

## Setup

### Venv
Start pyenv:
```sh
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Make venv:
```sh
pyenv virtualenv 3.10-dev cc310 && \
  pyenv activate cc310
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
