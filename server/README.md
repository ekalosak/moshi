# ui
The browser-based user interface for [Moshi](../README.md).

# Architecture
Frontend in TypeScript; backend in Python.
As such, the two project subdirectories are:
- `server/`
- `client/`

# Usage

## Server
Run the web server with:
```sh
flask --app server.main run
```

# Development

## Setup

### Python
Make a virtual environment and install the `server` project with dependencies:
```bash
pip install -e .
```
This will install the python dependencies from `pyproject.toml`.

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

## Build

### TypeScript
Build the project:
```bash
npx tsc -p client/tsconfig.json
```
The build artifacts should be in the same directory: `client/hello.js`.
