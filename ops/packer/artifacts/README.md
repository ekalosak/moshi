# entrypoint.sh
Used on the Moshi VM to launch the server.

### num workers in entrypoint.sh
gunicorn workers 3 because wrk=2xCore+1
https://docs.gunicorn.org/en/stable/design.html#how-many-workers