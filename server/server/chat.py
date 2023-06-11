""" This module implements a Chatter for use in the WebRTC server. """
import asyncio
import itertools
import os

from av import AudioFrame
from loguru import logger

from server import audio, speech
from moshi import Role, Message, lang, think
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
        self.language = None
        self.__task = None

    @logger.catch
    async def start(self):
        if self.__task is not None:
            logger.debug("Task already started, no-op")
            return
        logger.debug("Starting detector...")
        await self.detector.start()
        logger.debug("Detector started!")
        self.__task = asyncio.create_task(
            self.__run(),
            name="Main chat task"
        )

    @logger.catch
    async def stop(self):
        await self.detector.stop()
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        self.__task = None

    @logger.catch
    async def __run(self):
        """ Run the main program loop. """
        self._splash("moshi")
        for i in itertools.count():
            if i == MAX_LOOPS and MAX_LOOPS != 0:
                logger.info(f"Reached MAX_LOOPS: {MAX_LOOPS}, i={i}")
                break
            logger.debug(f"Starting loop number: i={i}")
            try:
                await self.__main()
            except KeyboardInterrupt as e:
                logger.debug(f"Got quit signal, exiting gracefully: {e}")
                break
        self._splash("bye")

    async def __main(self):
        """ Run one loop of the main program. """
        # TODO chat response and speech synthesis and language detection in between these two:
        # TODO when you do this, make sure to adapt the test_chatter_happy_path so it monkeypatches the openai
        logger.debug(f"Detecting user utterance...")
        usr_audio: AudioFrame = await self.detector.get_utterance()
        usr_text: str = await self.__transcribe_audio(usr_audio)
        await self.__detect_language(usr_text)
        await self.__get_response()
        ast_audio = self.__synth_speech()
        await self.responder.send_utterance(ast_audio)

    def set_utterance_channel(self, channel):
        if self.__channel is not None:
            raise ValueError(f"Already have an utterance channel: {self.__channel.label}:{self.__channel.id}")
        self.__channel = channel

    def __synth_speech(self) -> AudioFrame:
        msg = self.messages[-1]
        logger.debug(f"Synthesizing to speech: {msg}")
        assert msg.role == Role.AST
        frame = speech.synthesize_language(msg.content)
        logger.debug(f"Speech synthesized: {frame}")
        return frame

    async def __get_response(self):
        logger.debug(f"Responding to user text: {self.messages[-1]}")
        ast_txt: str = await asyncio.to_thread(
            think.completion_from_assistant,
            self.messages,
        )
        message = Message(Role.AST, ast_txt)
        self.messages.append(message)

    async def __transcribe_audio(self, audio, role=Role.USR):
        logger.debug(f"Transcribing {role.value} audio: {audio}")
        transcript: str = await speech.transcribe(audio)
        logger.info(f"Transcribed {role.value} utterance: {transcript}")
        message = Message(Role.USR, transcript)
        self.messages.append(message)
        return transcript

    async def __detect_language(self, text: str):
        """ Using the user's utterance text, determine the language they're speaking. """
        if self.language:
            logger.debug(f"Language already detected: {self.language}")
            return
        self.language = await asyncio.to_thread(
            lang.recognize_language,
            text,
        )
        logger.info(f"Language detected: {self.language}")
