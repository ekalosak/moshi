# entrypoint.sh
## num workers
gunicorn workers 3 because wrk=2xCore+1
https://docs.gunicorn.org/en/stable/design.html#how-many-workers
