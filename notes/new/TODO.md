# TODO
No Jira so ... this!

## In progress
u. refactor A. kill cli

## Backlog
i. core A. core functionality
i. core B. cleanup
    a. cleanup responses from chat
    b. add env var control over all various models, timeouts, and token limits
    c. lint
ii. web A. adapt chatter
    c. chat response text -> chat audio
    d. chat audio -> client audio track
    e. auth page & session cookies
    f. test multi-user
    g. serve behind nginx
    h. serve behind nginx on t2.micro
    i. setup the NAT gateway *early alpha available* using AWS endpoint (no registered domain)
    j. dashboard metrics & logs, setup alerts -> text and email me
    h. budget alerts

### P4
- Have the client.js ping over the `utterance` data channel for the transcript
    - see the `keepalive` data channel in client.js for how to
    - add a text box for the `status: ` prefixed messages
    - when you get a `transcript: ` prefixed message, add it to the `utterance-transcript` div

## Done
ii. web A. adapt chatter
    a. client web mic -> server audio track -> utterance audio frame extracted
    b. utterance text -> chat response text
    c. chat response text -> chat audio
    d. chat audio -> client audio track
