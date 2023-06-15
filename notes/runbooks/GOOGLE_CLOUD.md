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
    - Fill it out without callback urls

# Hosting

For GC's App Engine. NOTE: you can't delete the `default` service, if you goof it, you will have to delete the whole
Project. That's where `moshi-001` went, so be careful.
1. Ensure requirements.txt specified
    - https://cloud.google.com/docs/buildpacks/python#specifying_dependencies_with_pip
2. With the project already set up, app.yaml etc.
    - https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service
