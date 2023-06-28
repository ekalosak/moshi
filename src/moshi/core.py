"""This module implements the core WebRTCChatter class for use in the WebRTC server."""
import asyncio
import itertools
import os
import textwrap

from aiortc import RTCDataChannel
from av import AudioFrame
from loguru import logger

from moshi import (Message, Role, UserResetError, character, detector, lang, responder, speech, think, util)

STOP_TOKENS = ["user:"]
logger.info(f"Using STOP_TOKENS={STOP_TOKENS}")
MAX_RESPONSE_TOKENS = int(os.getenv("MOSHIMAXTOKENS", 64))
logger.info(f"Using MAX_RESPONSE_TOKENS={MAX_RESPONSE_TOKENS}")
CONNECTION_TIMEOUT = int(os.getenv("MOSHICONNECTIONTIMEOUT", 5))
logger.info(f"Using (WebRTC session) CONNECTION_TIMEOUT={CONNECTION_TIMEOUT}")
MAX_LOOPS = int(os.getenv("MOSHIMAXLOOPS", 10))
assert MAX_LOOPS >= 0
logger.info(f"Using MAX_LOOPS={MAX_LOOPS}")

logger.success("Loaded!")

def _init_messages() -> list[Message]:
    messages = [
        Message(
            Role.SYS,
            "You are a conversational partner for helping language learners practice a second language.",
        ),
        Message(
            Role.SYS,
            "DO NOT provide a translation. Respond in the language the user speaks unless asked explicitly for a translation.",
        ),
        Message(
            Role.SYS,
            "In the conversation section, after these instructions, DO NOT break character.",
        ),
    ]
    return messages

class WebRTCChatter:
    """This class does two important things:
    1. Coordinates the detector and responder, and
    2. Adapts the moshi.CliChatter for use in the WebRTC server.
    """

    def __init__(self, user_email: str):
        self.user_email = user_email
        self.messages = _init_messages()
        self.character: character.Character = None
        self.__task = None
        self.__channels = {}
        self.__connected = asyncio.Event()
        self.__status_and_transcript_channels_connected = asyncio.Event()
        self.detector = (
            detector.UtteranceDetector(self.__connected)
        )  # get_utterance: track -> AudioFrame
        self.responder = (
            responder.ResponsePlayer()
        )  # play_response: AudioFrame -> track

    @logger.catch
    async def start(self):
        if self.__task is not None:
            logger.debug("Task already started, no-op")
            return
        logger.debug("Starting detector...")
        await self.detector.start()
        logger.info("Detector started!")
        self.__task = asyncio.create_task(self.__run(), name="Main chat task")

    @logger.catch
    async def stop(self):
        await self.detector.stop()
        await self.__send_status("Disconnecting...")
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        self.__task = None

    async def connected(self):
        logger.debug("RTCPeerConnection status 'connected', waiting for status and transcript channels...")
        await asyncio.wait_for(
            self.__status_and_transcript_channels_connected.wait(),
            timeout=CONNECTION_TIMEOUT,
        )
        self.__connected.set()

    def add_channel(self, channel: RTCDataChannel):
        self.__channels[channel.label] = channel
        logger.info(f"Added a channel: {channel.label}:{channel.id}")
        if "status" in self.__channels and "transcript" in self.__channels:
            self.__status_and_transcript_channels_connected.set()
            logger.success("Status and transcript channels initialized!")
            self.__send_status("Connected!")

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
        with logger.contextualize(email=self.user_email):
            try:
                await asyncio.wait_for(self.__connected.wait(), timeout=CONNECTION_TIMEOUT)
            except asyncio.TimeoutError:
                logger.error(f"TimeoutError: CONNECTION_TIMEOUT={CONNECTION_TIMEOUT}")
                await self.__send_status("Timed out while establishing connection, try refreshing the page.")
            for i in itertools.count():
                if i == MAX_LOOPS and MAX_LOOPS != 0:
                    logger.info(f"Reached MAX_LOOPS: {MAX_LOOPS}, i={i}")
                    self.__send_status("Error: maximum conversation lenght reached, please refresh the page.")
                    break
                logger.debug(f"Starting loop number: i={i}")
                try:
                    await self.__main()
                except UserResetError as e:
                    self.__send_status(f"Error: {str(e)}\n\tPlease refresh the page")
                    break
            util.splash("bye")

    async def __main(self):
        """Run one loop of the main program."""
        usr_audio: AudioFrame = await self.__detect_user_utterance()
        self.__send_status("Transcribing...")
        usr_text: str = await self.__transcribe_audio(usr_audio)
        usr_msg = self.__add_message(usr_text, Role.USR)
        self.__send_transcript(usr_msg)
        await self.__init_character(sample_text=usr_text)
        self.__send_status("Thinking...")
        ast_text: str = await self.__get_response()
        if ast_text:
            ast_msg = self.__add_message(ast_text, Role.AST)
            self.__send_transcript(ast_msg)
            self.__send_status("Speaking...")
            ast_audio: AudioFrame = await self.__synth_speech()
            await self.__send_assistant_utterance(ast_audio)
        else:
            logger.warning("Got empty assistant response")
            raise UserResetError("I have nothing to say.")

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
        listening_callback = lambda msg: self.__send_status(msg)
        usr_audio: AudioFrame = await self.detector.get_utterance(listening_callback)
        logger.info(f"Detected user utterance: {usr_audio}")
        return usr_audio

    async def __send_assistant_utterance(self, ast_audio: AudioFrame):
        logger.debug(f"Sending assistant utterance: {ast_audio}...")
        await self.responder.send_utterance(ast_audio)
        logger.info("Sent assistant utterance.")

    def __add_message(self, content: str, role: Role) -> Message:
        assert isinstance(content, str)
        if not isinstance(role, Role):
            role = Role(role)
        msg = Message(role=role, content=content)
        logger.debug(f"Adding message: {msg}")
        self.messages.append(msg)
        return msg

    def __send_status(self, status: str):
        if channel := self.__channels.get("status"):
            logger.debug(f"Sending status: \"{status}\"")
            # NOTE channel.send does aio via ensure_future. Source: https://github.com/aiortc/aiortc/blob/main/src/aiortc/rtcsctptransport.py#L1796
            channel.send(status)
        else:
            logger.debug(f"channels: {self.__channels}")
            logger.warning(f"Dropping message because status channel not yet initialized: {status}")

    def __send_transcript(self, msg: Message):
        logger.debug(f"Sending transcript: {msg}")
        if channel := self.__channels.get("transcript"):
            match msg.role:
                case Role.USR:
                    name = "you  "
                case Role.AST:
                    name = "moshi"
                case _:
                    raise ValueError(f"role={msg.role} not supported, must be USR or AST")
            msg_str = f"{name}: {msg.content}"
            logger.debug(f"Sending transcript: \"{msg_str}\"")
            channel.send(msg_str)
        else:
            logger.warning(f"Dropping message because transcript channel not yet initialized: {msg}")

    async def __synth_speech(self, text: str=None) -> AudioFrame:
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
            max_tokens=MAX_RESPONSE_TOKENS,
            stop=STOP_TOKENS,
        )  # TODO add user=session["user id"] to help moderation
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
