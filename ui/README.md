# ui
The browser-based user interface for [Moshi](../README.md).

# Architecture
Frontend in TypeScript; backend in Python.

# Usage

## Server
Run the web server with:
```sh
flask --app ui.main run
```

# Development

## Setup

### Python
Make a virtual environment and install the `server` project with dependencies:
```bash
pip install -e .
```

### TypeScript

Install `npm`:
```bash
brew install npm
```

To install the project dependencies from `project.json`, run from this directory:
```bash
npm install
```

Sources:
- [TypeScript docs](https://www.typescriptlang.org/download)
