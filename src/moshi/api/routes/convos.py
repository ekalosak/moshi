
@app.get("/m/new/{kind}")
async def new_conversation(kind: str, user: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    unm = user['name']
    uid = user['uid']
    uem = user['email']
    logger.debug(f"Making new conversation of kind: {kind}")
    collection_ref = firestore_client.collection("conversations")
    convo = activities.new(kind=kind, uid=uid)
    doc_ref = collection_ref.document()
    cid = doc_ref.id
    with logger.contextualize(cid=cid):
        doc_data = convo.asdict()
        logger.debug(f"Creating conversation...")
        result = await doc_ref.set(doc_data)
        logger.info(f"Created new conversation document!")
    return {
        "message": "New conversation created",
        "detail" : {
            "conversation_id": cid,
        }
    }
