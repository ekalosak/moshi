""" This module implements a Chatter for use in the WebRTC server. """
import asyncio
import itertools
import os

from loguru import logger

from server import audio
from moshi import Role, Message
from moshi.chat import Chatter, _init_messages

MAX_LOOPS = int(os.getenv('MOSHIMAXLOOPS', 10))
assert MAX_LOOPS >= 0

class WebRTCChatter(Chatter):
    """ This class does two important things:
    1. Coordinates the detector and responder, and
    2. Adapts the moshi.CliChatter for use in the WebRTC server.
    """
    def __init__(self):
        self.detector = audio.UtteranceDetector()  # get_utterance: track -> AudioFrame
        self.responder = audio.ResponsePlayer()  # play_response: AudioFrame -> track
        self.messages = _init_messages()
        self.__language = None
        self.__user_audio = None
        self.__user_text = None
        self.__assistant_audio = None
        self.__assistant_text = None
        self.__task = None

    async def start(self):
        if self.__task is not None:
            logger.debug("Task already started, no-op")
            return
        logger.debug("Starting detector...")
        await self.detector.start()
        logger.debug("Detector started!")
        self.__task = asyncio.create_task(
            self._run(),
            name="Main chat task"
        )

    async def stop(self):
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        self.__task = None
        await self.detector.stop()

    async def _run(self):
        """ Run the main program loop. """
        self._splash("moshi")
        for i in itertools.count():
            if i == MAX_LOOPS and MAX_LOOPS != 0:
                logger.info(f"Reached MAX_LOOPS: {MAX_LOOPS}, i={i}")
                break
            logger.debug(f"Starting loop number: i={i}")
            try:
                await self._main()
            except KeyboardInterrupt as e:
                logger.debug(f"Got quit signal, exiting gracefully: {e}")
                break
        # self._report()
        self._splash("bye")

    async def _main(self):
        """ Run one loop of the main program. """
        # TODO chat response and speech synthesis and language detection in between these two:
        # TODO when you do this, make sure to adapt the test_chatter_happy_path so it monkeypatches the openai
        ut: AudioFrame = await self.detector.get_utterance()
        await asyncio.sleep(1)
        await self.responder.send_utterance(ut)
        await asyncio.sleep(1)
        # TODO use self._ methods rather than detector and responder directly; once this simplified demo works

    def set_utterance_channel(self, channel):
        if self.__channel is not None:
            raise ValueError(f"Already have an utterance channel: {self.__channel.label}:{self.__channel.id}")
        self.__channel = channel

    async def _get_user_utterance_audio(self):
        """ From the audio track, get an AudioFrame utterance from the client microphone. """
        self.__user_audio = await self.detector.get_utterance()

    async def _transcribe_user_utterance_audio_to_text(self):
        self.__user_text = await listen.transcribe_audio(self.__user_audio)
        message = Message(Role.USR, self.__user_text)
        logger.debug(message)
        self.messages.append(message)

    async def _get_assistant_response_text(self):
        """ From the AI assistant, get a text chat response to the user utterance text. """
        self.__assistant_text = await think.completion_from_assistant(self.messages)
        message = Message(Role.AST, self.__assistant_text)
        logger.debug(message)
        self.messages.append(message)

    async def _say_assistant_response_audio(self):
        """ Using the AI assistant's text response, synthesize speech and send the audio over the track to the client speaker. """
        self.__assistant_audio = await speech.synthesize(self.__assistant_text)
        await self.responder.send_audio(self.__assistant_audio)

    async def _detect_language(self):
        """ Using the user's utterance text, determine the language they're speaking. """
        if self.language:
            logger.debug(f"Language already detected: {self.language}")
            return
        self.language = await lang.recognize_language(self.__user_text)
        logger.info(f"Language detected: {self.language}")
