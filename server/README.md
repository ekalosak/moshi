# server
This project provides the server for the browser-based user interface for [Moshi](../README.md).

# Architecture
- Flask for the server.
- Websockets for the streaming.
- Javascript for the frontend.

# Usage
Run the web server with:
```sh
gunicorn -k gevent -w 1 server.main:app
```

# Development

## Setup
```bash
pip install -e .
```

## Usage
Run the development web server with:
```sh
flask --app server.main run
```

Or:
```sh
gunicorn -k gevent -w 1 server.main:app --reload -b localhost:5000 -t 2
```

Navigate to `localhost:5000` in the browser.
