# server
This project provides the server for the browser-based user interface for [Moshi](../README.md).

# Architecture
- Flask for the server.
- Websockets for the streaming.
- Javascript for the frontend.

# Development

## Setup
```bash
pip install -e .
```

## Usage
Run the web server with:
```sh
flask --app server.main run
```

Navigate to `localhost:5000` in the browser.
