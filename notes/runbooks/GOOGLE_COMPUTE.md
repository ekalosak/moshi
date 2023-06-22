# Why Compute Engine?
App Engine is simpler for "just run my Flask app". But its networking is obscured by the "magic" they do to enable the
ease-of-use. Though they do allow WebSockets, that's TCP (so any packet loss on the network is going to gargantuanly
affect latency). WebRTC is UDP.

The other options for hosting a web service on GCP are Kubernetes Engine and Compute Engine. Kubernetes is for scaling.
So CE.

# Required APIs to enable
- Compute Engine
- Secret Manager
- Cloud NAT
- Cloud VPC

# I bought a domain
1. Get a domain from Google Domains
2. Import it into Cloud Domains

# Spin up an instance
From the [console](https://console.cloud.google.com/compute/instancesAdd?project=moshi-002), I launched this:
```sh
NAME=instance-003 \
ZONE=us-east1-b \
gcloud compute instances create $NAME \
    --project=moshi-002 \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=462213871057-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --tags=https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=$NAME,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230615,mode=rw,size=10,type=projects/moshi-002/zones/us-west4-b/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any
```
In `us-east-1` it costs $7.11/mo (subregion `us-east-1b`).

## Connect
```sh
NAME=instance-003 \
ZONE=us-east1-b \
gcloud compute ssh \
    --project=moshi-002 \
    --zone=$ZONE \
    $NAME
```

## Copy image build files
```sh
NAME=instance-003 \
gcloud compute scp ./ops/*.sh $NAME:/home/eric
```

## Build the image's prototype VM
ssh and:
```bash
./setup.sh
source .bashrc
nohup ./install.sh &
```
Walk away, let Python compile.
Check is it running: `ps aux | grep install.sh`
Check logs: `tail -f nohup.out`

Make sure the venv and moshi are all gucci.

## Create the image
1. Take a snapshot of the VM
2. Create image from VM from the snapshot

## IAM
Make a Service Account with the following Roles:
- Arifact Registry Reader
- Secret Manager Secret Accessor

Shut down the VM and apply the Role in the edit menu.

## Create the instance template from the image
Super easy just make sure to edit the boot disk to point to the Image created from the Snapshot.
```bash
gcloud compute instance-templates create instance-template-2 --project=moshi-002 --machine-type=e2-micro --network-interface=network=default,network-tier=PREMIUM --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=gce-1-326@moshi-002.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --tags=allow-health-check --create-disk=auto-delete=yes,boot=yes,device-name=instance-template-2,image=projects/moshi-002/global/images/image-2,mode=rw,size=10,type=pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
```
Note that I am using the allow-health-check network tag as the guide specifies.

## Create instance group
https://cloud.google.com/load-balancing/docs/https/setup-global-ext-https-compute
1. Easy, defaults except add named port `http` with number `80`.

## Reserve and external IP
https://console.cloud.google.com/networking/addresses/
1. Easy, make sure it's "global"

# Port forward and try it out

# Set up the VPC
The CE has a default VPC.
For this project, WebRTC requires UDP traffic over some ports.

# Set up the NAT gateway
Defaults are good - the only thing to double check is that you have, in the advanced settings:
- Static Port Allocation (NOT Dynamic, i.e. leave unchecked.)
- Endpoint-Independent Mapping (i.e. check the box.)
Sources:
    - https://cloud.google.com/nat/docs/ports-and-addresses

# Get SSL credentials
```sh
gcloud compute ssl-certificates create ssl-cert-001 \
    --domains="chatmoshi.com" \
    --global
```

# Network LB vs Application LB?
Use ALB for HTTPS (SSL, signalling) and NLB for UDP (DTLS, media stream).
Sources:
    - https://cloud.google.com/iap/docs/load-balancer-howto
    - https://cloud.google.com/load-balancing/docs/load-balancing-overview
    - https://cloud.google.com/sdk/gcloud/reference/compute/ssl-certificates

## How to set up
1. SSL cert (above)
2. CE instance (previous setup)
3. CE instance group (https://console.cloud.google.com/compute/instanceGroups/add?authuser=1&project=moshi-002)

## NLB type
- https://cloud.google.com/load-balancing/docs/passthrough-network-load-balancer

# Yep we're encrypting UDP
Sources:
    - https://webrtc-security.github.io/
    - http://ithare.com/udp-for-games-security-encryption-and-ddos-protection/
    - https://aiortc.readthedocs.io/en/latest/api.html#datagram-transport-layer-security-dtls
    - https://github.com/aiortc/aiortc/blob/9f14474c0953b90139c8697a216e4c2cd8ee5504/src/aiortc/rtcpeerconnection.py#LL1081C15-L1081C15
        - also L1085-1086

# SSH to CE VM
```
gcloud compute ssh --project=moshi-002 \
    --zone=us-east1-b \
    moshi-002-instance-001
```

# Connect to VPC w Chrome
```sgh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --user-data-dir="$HOME/chrome-proxy-profile" \
        --proxy-server="socks5://localhost:1080"
```
- https://cloud.google.com/solutions/connecting-securely#chrome

# CE setup
See ops/setup.sh for Deterministic Instance Template setup script.
```
./setup.sh
source .bashrc
nohup ./install.sh &
```
