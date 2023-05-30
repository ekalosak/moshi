# ui
The browser-based user interface for [Moshi](../README.md).

# Usage
Run the web server with:
```sh
flask --app ui.main run
```

# Development

## Elm

### Setup Elm
Install Elm compiler, then make project artifacts:
```sh
mkdir elm && cd elm && elm init
```

### Compile Elm
```sh
elm make src/Main.elm --optimize
```

Also note there's a REPL: `elm repl`.

### Quickstart
```
elm reactor
```

# Sources
- https://github.com/hypebeast/flask-elm-starter-kit/
