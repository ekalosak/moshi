"""
Web server using aiortc and Flask to receive client microphone audio.

The server creates a Flask web application that handles two routes:
- '/' serves the home page that initiates the microphone audio streaming.
- '/offer' receives the client's SDP offer, establishes a peer connection using aiortc,
  and starts consuming the client's microphone audio.

Dependencies:
- aiortc: Async WebRTC and ORTC implementation
- Flask: A micro web framework for Python

Example usage:
1. Start the server: python rtc.py
2. Open a browser and navigate to http://localhost:5000
3. Grant access to the microphone when prompted.
4. The server will receive the client's microphone audio and print any data channel messages.

Note: This is a basic example and may require modifications for more complex scenarios or additional functionality.
"""
import asyncio
import aiortc
from aiortc.contrib.media import MediaPlayer
from flask import Flask, render_template, Response
from loguru import logger

app = Flask(__name__)
loop = asyncio.get_event_loop()
pc = None

@app.route('/')
def index():
    return render_template('demo_rtc.html')

@app.route('/offer', methods=['POST'])
def offer(request):
    global pc

    async def consume_audio(track):
        player = MediaPlayer(track)
        while True:
            frame = await player.read()
            if frame is None:
                break

    async def answer(request):
        offer = await request.json()
        pc = await create_peer_connection()

        @pc.on("track")
        async def on_track(track):
            if track.kind == "audio":
                pc.addTrack(track)
                await consume_audio(track)

        await pc.setRemoteDescription(aiortc.sdp.SDPType.OFFER, offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return Response(answer.sdp, content_type='application/json')

    return loop.run_until_complete(answer(request))

async def create_peer_connection():
    config = aiortc.RTCConfiguration()
    pc = aiortc.RTCPeerConnection(configuration=config)
    pc.createDataChannel('data')

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            print("Received message:", message)

    return pc

if __name__ == '__main__':
    logger.info('Starting server...')
    try:
        app.run()
    except Exception as e:
        logger.error(f"Terminated with error: {e}")
    else:
        logger.success("Terminated gracefully.")
