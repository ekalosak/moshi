# server
This project provides the server for the browser-based user interface for [Moshi](../README.md).

# Architecture
- Flask for the server.
- Javascript for the frontend.
- Websockets for the streaming.

# Usage

```bash
gunicorn server.main:app --worker-class gevent --bind 127.0.0.1:5000
```

# Development

## Setup

### Python Flask server
Make a virtual environment and install the `server` project with dependencies:
```bash
pip install -e .
```
This will install the python dependencies from `pyproject.toml`.

## Development server
Run the web server with:
```sh
flask --app server.main run
```
