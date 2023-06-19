# Why get a TURN server?
To make ICE work behind a Symmetric NAT, STUN (public IP exchange) is insufficient.
Thus, a TURN (packet relay) is required.

## Options
- Roll my own (coturn)
- Twillio
- Metered

## I picked Metered
50GB/mo free, no lost time for deployment / maintenance. Easy win.

# Dashboard
https://dashboard.metered.ca/turnserver/app/6490885575fcccd41948af78

# Setup Runbook
1. `https://metered.ca`, sign up, really fucking easy.
2. Get API key and put into gcloud secrets-manager.
    - domain: `moshi.metered.ca`, key: `******`
    - https://console.cloud.google.com/security/secret-manager/create?project=moshi-002
    - secret id: `metered-turn-server-api-key-001`
3. In code, get secret from manager, get creds using secret from metered.ca, then formulate those into aiortc.RTCIceSeerver objects.
