# 🧑💬🤖 moshi
Have a spoken conversation in another language, at your level.

# Architecture
- `moshi` the core functionality.
- `ui` the frontend and server that plug `moshi` into the browser.

# Development

## Development docs
- `planning/` has some product content and design proposals.
- [`DESIGN.md`](DESIGN.md) has the overall product design.

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
mkdir egg && \
    pip install -e moshi[dev,test]
```
Note that the `setup.cfg` puts the `.egg-info` into the local `./egg` directory; you have to create the `egg` dir first.

## Docs
```
python -m pydoc -b
```

# Usage
Usage instructions for each constituent project are provided in the corresponding project subdirectory e.g.
[`moshi/README.md`](moshi/README.md).
