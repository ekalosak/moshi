# Setup account and project

1. Make account
    a. Put in credit card, but 3mo free $300
2. Make project
    a. Moshi
    b. Service Account is `moshi-001`

# Setup dev machine

3. Install `gcloud`
    a. https://cloud.google.com/sdk/docs/install
    b. `gcloud init`
    c. `gcloud config set project moshi-002`
    d. https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to
4. Credential discovery should be automatic when logged in via cli
    a. `gcloud auth application-default login`
    b.  https://googleapis.dev/python/google-api-core/latest/auth.html

# Enable Google API endpoints

1. Enable translation.googleapis.com
    - https://console.cloud.google.com/marketplace/product/google/translate.googleapis.com
2. Enable texttospeech.googleapis.com
    - https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com
3. Enable OAuth2
    - https://console.cloud.google.com/apis/credentials/consent
        - Fill it out without any of the URLs
    - Console: https://console.cloud.google.com/apis/credentials/oauthclient
        - Add credential > Oauth client ID > web app > redirect url `http://localhost:8080`
        - Docs: https://developers.google.com/identity/protocols/oauth2/web-server

# Hosting

For GC's App Engine. NOTE: you can't delete the `default` service, if you goof it, you will have to delete the whole
Project. That's where `moshi-001` went, so be careful.
1. Ensure requirements.txt specified
    - https://cloud.google.com/docs/buildpacks/python#specifying_dependencies_with_pip
2. With the Project already set up, add app.yaml
    - https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service
    - see demo/
3. `.gcloudignore`
4. `gcloud app deploy` from directory containing app.yaml

## Run demo server locally before `app deploy`
- https://cloud.google.com/appengine/docs/standard/tools/using-local-server?tab=python#set-up
- `gcloud components install app-engine-python` to install the dev server
- `gcloud info` to get the `CLOUD_SDK_ROOT`
    - `set -x CLOUD_SDK_ROOT /Users/eric/bin/google-cloud-sdk`

Add `Procfile` becazuse vanilla gunicorn invocation won't work:
- https://cloud.google.com/docs/buildpacks/python?authuser=1#application_entrypoint
- https://docs.aiohttp.org/en/stable/deployment.html#start-gunicorn

Make sure py3 and py27 are available globally.
```sh
pyenv deactivate && \
    pyenv global 3.7.4 2.7.18
```

Run the demo server from the moshi/ dir where the app.py lives.
```sh
set -x CLOUD_SDK_ROOT /Users/eric/bin/google-cloud-sdk
set -x GOOGLE_CLOUD_PROJECT moshi-002
python3 $CLOUD_SDK_ROOT/bin/dev_appserver.py \
    --runtime_python_path="python3=/Users/eric/.pyenv/shims/python3,python27=/Users/eric/.pyenv/shims/python2" \
    app.yaml
```
