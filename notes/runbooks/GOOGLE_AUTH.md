# Adding an OAuth2 button to the webpage
1. Configure an OAuth consent screen
1. Make an auth credential
    - https://console.cloud.google.com/apis/credentials/oauthclient/
3. Add your whitelisted domains to the credential:
    - localhost (for testing) with and without a port specified
    - your free App Engine URL
    - your purchased domain URL
