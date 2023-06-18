# Adding an OAuth2 button to the webpage
1. Configure an OAuth consent screen
1. Make an auth credential
    - https://console.cloud.google.com/apis/credentials/oauthclient/
3. Add your whitelisted domains to the credential:
    - localhost (for testing) with and without a port specified
    - your free App Engine URL
    - your purchased domain URL
4. If you don't see the button on the public page, check the dev console:
    - If you see `GSI_LOGGER ... Unsecured login_uri ...` you need to make sure the public page (not localhost) has an
      https redirect - Google won't even load the button when the redirect is insecure.
