# Setup runbook

1. Make account
    a. Put in credit card, but 3mo free $300
2. Make project
    a. Moshi
    b. Service Account is `moshi-001`
3. Enable translation.googleapis.com
4. Enable texttospeech.googleapis.com
5. Download API key, restrict its access to translation and texttospeech, put in ~/.gcloud, loaded by fish into env
6. Credential discovery should be automatic
    a. `GCLOUD_API_KEY` env var
    b.  https://googleapis.dev/python/google-api-core/latest/auth.html
7. Installed `gcloud`
    a. https://cloud.google.com/sdk/docs/install
8. `gcloud config set project moshi-001`
9. Authenticate `gcloud auth application-default login`
    a. Opens web browser, do login flow.
    b. https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to
