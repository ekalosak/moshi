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

# Python Artifact Repo

1. Enable Artifact API
    - https://console.cloud.google.com/apis/enableflow?apiid=artifactregistry.googleapis.com
2. `pip install twine`
3. Run the following to make a repo:
```sh
gcloud artifacts repositories create moshi-002-repo \
    --repository-format=python \
    --location=us-east1 \
    --description="Moshi project Python repository"
```
4. Set the repo & loc:
```fish
gcloud config set artifacts/repository moshi-002-repo && \
    gcloud config set artifacts/location us-east1
```
5. Build the wheel:
```fish
mkdir build
pip install build && \
    python -m build
```
6. Authenticate to GC PyPi
    a. `pip install keyring`
    b. `pip install keyrings.google-artifactregistry-auth`
    c. verify: `keyring --list-backends`
    d. prep the settings:
    ```fish
    set -x GOOGLE_CLOUD_LOCATION us-central1
    gcloud artifacts print-settings python --project=$GOOGLE_CLOUD_PROJECT \
        --repository=$GOOGLE_CLOUD_PYPI_NAME \
        --location=$GOOGLE_CLOUD_LOCATION
    ```
    e. Update ~/.pypirc and ~/.config/pip/pip.conf
    f. Following https://stackoverflow.com/a/68998902 `gcloud auth revoke --all` to clean creds
    g. `gcloud auth application-default login`
    h. `pip install keyrings.google-artifactregistry-auth` and hit enter
7. Upload the package:
```fish
set -x GOOGLE_CLOUD_PROJECT moshi-3
set -x GOOGLE_CLOUD_PYPI_NAME moshi
set -x GOOGLE_CLOUD_PYPI_URL https://us-central1-python.pkg.dev/$GOOGLE_CLOUD_PROJECT/$GOOGLE_CLOUD_PYPI_NAME/
python3 -m twine upload \
    --repository-url $GOOGLE_CLOUD_PYPI_URL \
    "dist/*"
```
