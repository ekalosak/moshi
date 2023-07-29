"""This module implements the core WebRTCChatter class for use in the WebRTC server."""
import asyncio
import itertools
import os
import textwrap

from aiortc import RTCDataChannel
from aiortc.mediastreams import MediaStreamError
from av import AudioFrame
from loguru import logger

from moshi import (
    Message,
    Role,
    UserResetError,
    utils,
)
from moshi.core import (
    character,
)
from . import (
    detector,
    responder,
    speech,
    think,
)

MAX_RESPONSE_TOKENS = 64
MAX_LOOPS = 30
STOP_TOKENS = ["user:"]
UTT_START_MAX_COUNT = 2
assert MAX_LOOPS >= 0

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

    def __init__(self, user_email: str = "none"):
        self.__dc = None
        self.__dc_connected = asyncio.Event()
        self.__task = None
        self.__utt_start_count = 0
        self.character: character.Character = None
        self.logger = logger.bind(email=user_email)
        self.messages = _init_messages()
        self.detector = detector.UtteranceDetector()  # get_utterance: track -> AudioFrame
        self.responder = responder.ResponsePlayer()  # play_response: AudioFrame -> track

    def __send(self, msg: str):
        """Send msg over dc with best effort."""
        # NOTE RTCDataChannel.send() does aio via ensure_future.
        # source: https://github.com/aiortc/aiortc/blob/main/src/aiortc/rtcsctptransport.py#L1796
        self.logger.debug('sending: ' + msg)
        if not self.__dc:
            self.logger.warning(f"tried to send before dc connected, discarding message: {msg}")
            return
        self.__dc.send(msg)

    def _send_status(self, status: str):
        self.__send(f"status {status}")

    def _send_error(self, err: str):
        self.logger.error("Sending error to user: " + err)
        self.__send("error " + err)

    def _send_transcript(self, msg: Message):
        if msg.role == Role.SYS:
            raise ValueError(
                f"{msg.role} not supported user-facing transcript Role, must be USR or AST"
            )
        self.__send('transcript ' + f"{msg.role.value} {msg.content}")

    async def _speak_to_user(self, text: str):
        """Speak to the user over audio channel.
        Use the user's configured language, and provide some variety in phrasing.
        """
        self.logger.warning("TODO")
        await asyncio.sleep(0)

    async def start(self):
        if self.__task:
            self.logger.debug("Already started, no-op.")
            return
        self.__task = asyncio.create_task(self.__run(), name="Main chat task")
        await self.wait_dc_connected()
        self._send_status("start")
        logger.info("Started")

    async def stop(self):
        if self.__task == None:
            self.logger.warning("Already stopped, no-op.")
        self._send_status("stop")
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        await self.__task
        self.__task = None
        logger.info("Stopped")

    async def wait_dc_connected(self):
        self.logger.debug("pc connected, awaiting dc...")
        await self.__dc_connected.wait()
        self.logger.debug("dc connected.")

    def add_dc(self, dc: RTCDataChannel):
        if self.__dc is not None:
            raise ValueError("DataChannel already set")
        self.__dc = dc
        self.__dc_connected.set()
        self.logger.success(f"dc connected: {dc.label}:{dc.id}")

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
        utils.log.splash("moshi")
        await self.__dc_connected.wait()
        self._send_status("hello")
        for i in itertools.count():
            if i == MAX_LOOPS and MAX_LOOPS != 0:
                msg = f"Reached MAX_LOOPS={MAX_LOOPS}, i={i}"
                self.logger.info(msg)
                self._send_status("maxlen", msg)
                break
            self.logger.debug(f"Starting loop {i}")
            with self.logger.contextualize(i=i):
                self._send_status("loopstart")
            try:
                await self.__main()
            except UserResetError as e:
                self._send_error(str(e))
                self._send_status("bye")
                break
            except MediaStreamError:
                self.logger.info("User hung up (disconnect).")
                break
            except Exception as e:
                logger.error(e)
                self._send_error("internal")
                break
        await self.stop()
        util.splash("bye")

    async def __main(self):
        """Run one loop of the main program.
        Raises:
            - UserResetError when chatter entered into a state that requires reset by user.
            - MediaStreamError when connection error or user hangup (disconnect).
        """
        self.logger.debug("main")
        self._send_status("listening")
        try:
            # Raises: MediaStreamError, TimeoutError, UtteranceTooLongError
            usr_audio: AudioFrame = await self.detector.get_utterance()
        except detector.UtteranceTooLongError as e:
            self.logger.debug("Utterance too long, prompting user to try again.")
            await self._send_error("utttoolong")
            return
        except asyncio.TimeoutError as e:
            if self.__utt_start_count == UTT_START_MAX_COUNT:
                self.logger.debug("User didn't start speaking {self.__utt_start_count} times, raising.")
                raise UserResetError("usrNotSpeaking") from e
            self.logger.debug("Utterance too long, prompting user to try again.")
            await self._speak_to_user("Are you still there?")
            self.__utt_start_count += 1
            return

        self.__utt_start_count = 0
        self._send_status("transcribing")
        usr_text: str = await self.__transcribe_audio(usr_audio)  # TODO handle network errors
        usr_msg = self.__add_message(usr_text, Role.USR)
        self._send_transcript(usr_msg)
        await self.__init_character(sample_text=usr_text)
        self._send_status("thinking")
        ast_text: str = await self.__get_response()
        if ast_text:
            ast_msg = self.__add_message(ast_text, Role.AST)
            self._send_transcript(ast_msg)
            self._send_status("speaking")
            ast_audio: AudioFrame = await self.__synth_speech()  # TODO handle network errors
            await self.responder.send_utterance(ast_audio)  # TODO handle: Raises: MediaStreamError, TimeoutError
        else:
            self.logger.warning("Got empty assistant response")
            raise UserResetError("empty assistant response")

    async def __init_character(self, sample_text: str):
        """Using the sample text, initialize the voice and language used by Chatter."""
        if self.character is not None:
            return
        language = await utils.lang.detect_language(sample_text)
        self.logger.debug(f"Language detected: {language}")
        voice = await speech.get_voice(language)
        self.logger.debug(f"Selected voice: {voice}")
        self.character = character.Character(voice, language)
        self.logger.info(f"Initialized character: {self.character}")

    def __add_message(self, content: str, role: Role) -> Message:
        # TODO write the message to Firebase
        assert isinstance(content, str)
        if not isinstance(role, Role):
            role = Role(role)
        msg = Message(role=role, content=content)
        self.logger.debug(f"Adding message: {msg}")
        self.messages.append(msg)
        return msg

    async def __synth_speech(self, text: str = None) -> AudioFrame:
        msg = self.messages[-1]
        self.logger.debug(f"Synthesizing to speech: {msg}")
        assert msg.role == Role.AST
        frame = await speech.synthesize_speech(msg.content, self.voice)
        self.logger.info(f"Speech synthesized: {frame}")
        assert isinstance(frame, AudioFrame)
        return frame

    async def __get_response(self):
        """Retrieve the chatbot's response to the user utterance."""
        usr_msg = self.messages[-1]
        assert usr_msg.content is self.user_utterance, "State is out of whack"
        self.logger.debug(f"Responding to user message: {usr_msg}")
        ast_txts: str = await think.completion_from_assistant(
            self.messages,
            n=1,
            max_tokens=MAX_RESPONSE_TOKENS,
            stop=STOP_TOKENS,
        )  # TODO add user=session["user id"] to help moderation
        assert len(ast_txts) == 1
        ast_txt = ast_txts[0]
        self.logger.info(f"Got assistant response: {textwrap.shorten(ast_txt, 64)}")
        return ast_txt

    async def __transcribe_audio(self, audio, role=Role.USR):
        self.logger.debug(f"Transcribing {role.value} audio: {audio}")
        transcript: str = await speech.transcribe(audio)
        self.logger.info(
            f"Transcribed {role.value} utterance: {textwrap.shorten(transcript, 64)}"
        )
        return transcript
