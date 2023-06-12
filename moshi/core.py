"""This module implements the core WebRTCChatter class for use in the WebRTC server."""
import asyncio
import itertools
import os
import textwrap

from av import AudioFrame
from loguru import logger

from moshi import speech, lang, think, util, Message, ResponsePlayer, Role, UtteranceDetector, MAX_LOOPS

logger.success("Loaded!")

def _init_messages() -> list[Message]:
    messages = [
        Message(
            Role.SYS,
            "You are a conversational partner for helping language learners practice spoken language.",
        ),
        Message(
            Role.SYS,
            "Do not provide a translation. Respond in the language the user speaks.",
        )
    ]
    return messages

class WebRTCChatter(Chatter):
    """This class does two important things:
    1. Coordinates the detector and responder, and
    2. Adapts the moshi.CliChatter for use in the WebRTC server.
    """
    def __init__(self):
        self.detector = UtteranceDetector()  # get_utterance: track -> AudioFrame
        self.responder = ResponsePlayer()  # play_response: AudioFrame -> track
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

    @property
    def user_utterance(self) -> str:
        """The latest user utterance."""
        logger.trace("\n" + pformat(self.messages))
        for msg in self.messages[::-1]:
            if msg.role == Role.USR:
                return msg.content
        raise ValueError("No user utterances in self.messages")

    @property
    def assistant_utterance(self) -> str:
        """The latest assistant utterance."""
        for msg in self.messages[::-1]:
            if msg.role == Role.AST:
                return msg.content
        raise ValueError("No assistant utterances in self.messages")

    @logger.catch
    async def __run(self):
        """ Run the main program loop. """
        util.splash("moshi")
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
        util.splash("bye")

    async def __main(self):
        """ Run one loop of the main program. """
        usr_audio: AudioFrame = await self.__detect_user_utterance()
        usr_text: str = await self.__transcribe_audio(usr_audio)
        await self.__detect_language(usr_text)
        await self.__get_response()
        ast_audio = self.__synth_speech()
        await self.responder.send_utterance(ast_audio)

    def set_transcript_channel(self, channel):
        if self.__channel is not None:
            raise ValueError(f"Already have a transcript channel: {self.__channel.label}:{self.__channel.id}")
        self.__channel = channel

    async def __detect_user_utterance(self) -> AudioFrame:
        logger.debug(f"Detecting user utterance...")
        usr_audio: AudioFrame = await self.detector.get_utterance()
        logger.info(f"Detected user utterance: {usr_audio}")
        return usr_audio

    def __add_message(self, content:str, role:Role):
        assert isinstance(content, str)
        if not isinstance(role, Role):
            role = Role(role)
        msg = Message(role=role, content=content)
        logger.debug(f"Adding message: {msg}")
        self.messages.append(msg)

    def __synth_speech(self) -> AudioFrame:
        msg = self.messages[-1]
        logger.debug(f"Synthesizing to speech: {msg}")
        assert msg.role == Role.AST
        frame = speech.synthesize_language(msg.content, self.language)
        logger.info(f"Speech synthesized: {frame}")
        return frame

    async def __get_response(self):
        logger.debug(f"Responding to user text: {self.messages[-1]}")
        ast_txts: str = await asyncio.to_thread(
            think.completion_from_assistant,
            self.messages,
            n=1,
        )
        assert len(ast_txts) == 1
        ast_txt = ast_txts[0]
        logger.info(f"Got assistant response: {textwrap.shorten(ast_txt, 64)}")
        self.__add_message(ast_txt, Role.AST)

    async def __transcribe_audio(self, audio, role=Role.USR):
        logger.debug(f"Transcribing {role.value} audio: {audio}")
        transcript: str = await speech.transcribe(audio)
        logger.info(f"Transcribed {role.value} utterance: {textwrap.shorten(transcript, 64)}")
        self.__add_message(transcript, Role.USR)
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
