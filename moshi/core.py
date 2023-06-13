"""This module implements the core WebRTCChatter class for use in the WebRTC server."""
import asyncio
import itertools
import os
import textwrap

from av import AudioFrame
from loguru import logger

from moshi import (Message, Role, character, detector, lang, responder, speech,
                   think, util)

MAX_LOOPS = int(os.getenv("MOSHIMAXLOOPS", 10))
assert MAX_LOOPS >= 0
logger.info(f"Running main loop max times: {MAX_LOOPS}")

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
        ),
    ]
    return messages


class WebRTCChatter:
    """This class does two important things:
    1. Coordinates the detector and responder, and
    2. Adapts the moshi.CliChatter for use in the WebRTC server.
    """

    def __init__(self):
        self.detector = (
            detector.UtteranceDetector()
        )  # get_utterance: track -> AudioFrame
        self.responder = (
            responder.ResponsePlayer()
        )  # play_response: AudioFrame -> track
        self.messages = _init_messages()
        self.character: character.Character = None
        self.__task = None

    @logger.catch
    async def start(self):
        if self.__task is not None:
            logger.debug("Task already started, no-op")
            return
        logger.debug("Starting detector...")
        await self.detector.start()
        logger.debug("Detector started!")
        self.__task = asyncio.create_task(self.__run(), name="Main chat task")

    @logger.catch
    async def stop(self):
        await self.detector.stop()
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        self.__task = None

    def set_transcript_channel(self, channel):
        if self.__channel is not None:
            raise ValueError(
                f"Already have a transcript channel: {self.__channel.label}:{self.__channel.id}"
            )
        self.__channel = channel

    @property
    def voice(self) -> object:
        return self.character.voice

    @property
    def language(self) -> str:
        return self.character.language

    @property
    def user_utterance(self) -> str:
        """The latest user utterance."""
        return self.__latest_msg(Role.USR).content

    @property
    def assistant_utterance(self) -> str:
        """The latest assistant utterance."""
        return self.__latest_msg(Role.AST).content

    def __latest_msg(self, role: Role) -> Message:
        for msg in self.messages[::-1]:
            if msg.role == role:
                return msg
        raise ValueError(f"No {role.value} utterances in self.messages")

    @logger.catch
    async def __run(self):
        """Run the main program loop."""
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
        """Run one loop of the main program."""
        usr_audio: AudioFrame = await self.__detect_user_utterance()
        usr_text: str = await self.__transcribe_audio(usr_audio)
        self.__add_message(usr_text, Role.USR)
        await self.__init_character(sample_text=usr_text)
        ast_text: str = await self.__get_response()
        self.__add_message(ast_text, Role.AST)
        ast_audio: AudioFrame = await self.__synth_speech()
        await self.__send_assistant_utterance(ast_audio)

    async def __init_character(self, sample_text: str):
        """Using the sample text, initialize the voice and language used by Chatter."""
        if self.character is not None:
            return
        language = await lang.detect_language(sample_text)
        logger.debug(f"Language detected: {language}")
        voice = await speech.get_voice(language)
        logger.debug(f"Selected voice: {voice}")
        self.character = character.Character(voice, language)
        logger.info(f"Initialized character: {self.character}")

    async def __detect_user_utterance(self) -> AudioFrame:
        logger.debug("Detecting user utterance...")
        usr_audio: AudioFrame = await self.detector.get_utterance()
        logger.info(f"Detected user utterance: {usr_audio}")
        return usr_audio

    async def __send_assistant_utterance(self, ast_audio: AudioFrame):
        logger.debug(f"Sending assistant utterance: {ast_audio}...")
        await self.responder.send_utterance(ast_audio)
        logger.info("Sent assistant utterance.")

    def __add_message(self, content: str, role: Role):
        assert isinstance(content, str)
        if not isinstance(role, Role):
            role = Role(role)
        msg = Message(role=role, content=content)
        logger.debug(f"Adding message: {msg}")
        self.messages.append(msg)

    async def __synth_speech(self) -> AudioFrame:
        msg = self.messages[-1]
        logger.debug(f"Synthesizing to speech: {msg}")
        assert msg.role == Role.AST
        frame = await speech.synthesize_speech(msg.content, self.voice)
        logger.info(f"Speech synthesized: {frame}")
        assert isinstance(frame, AudioFrame)
        return frame

    async def __get_response(self):
        """Retrieve the chatbot's response to the user utterance."""
        usr_msg = self.messages[-1]
        assert usr_msg.content is self.user_utterance, "State is out of whack"
        logger.debug(f"Responding to user message: {usr_msg}")
        ast_txts: str = await asyncio.to_thread(
            think.completion_from_assistant,
            self.messages,
            n=1,
        )
        assert len(ast_txts) == 1
        ast_txt = ast_txts[0]
        logger.info(f"Got assistant response: {textwrap.shorten(ast_txt, 64)}")
        return ast_txt

    async def __transcribe_audio(self, audio, role=Role.USR):
        logger.debug(f"Transcribing {role.value} audio: {audio}")
        transcript: str = await speech.transcribe(audio)
        logger.info(
            f"Transcribed {role.value} utterance: {textwrap.shorten(transcript, 64)}"
        )
        return transcript
