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
    util,
)
from moshi.chat import (
    character,
    detector,
    lang,
    responder,
    speech,
    think,
)

STOP_TOKENS = ["user:"]
logger.info(f"Using STOP_TOKENS={STOP_TOKENS}")
MAX_RESPONSE_TOKENS = int(os.getenv("MOSHIMAXTOKENS", 64))
logger.info(f"Using MAX_RESPONSE_TOKENS={MAX_RESPONSE_TOKENS}")
MAX_LOOPS = int(os.getenv("MOSHIMAXLOOPS", 30))
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

    def __init__(self, user_email: str = "none"):
        self.__dc = None
        self.__dc_connected = asyncio.Event()
        self.__tasks = []
        self.character: character.Character = None
        self.logger = logger.bind(email=user_email)
        self.messages = _init_messages()
        self.detector = detector.UtteranceDetector(
            self.wait_dc_connected,
            self._send_status,
        )  # get_utterance: track -> AudioFrame
        self.responder = responder.ResponsePlayer(
            self._send_status,
        )  # play_response: AudioFrame -> track

    def __send(self, msg: str):
        # NOTE RTCDataChannel.send() does aio via ensure_future.
        # source: https://github.com/aiortc/aiortc/blob/main/src/aiortc/rtcsctptransport.py#L1796
        self.logger.debug('sending: ' + msg)
        self.__dc.send(msg)

    def _send_status(self, status: str):
        self.__send("status " + status)

    def _send_error(self, err: str):
        self.logger.error("Sending error to user: " + err)
        self.__send("error " + msg)

    def _send_transcript(self, msg: Message):
        if msg.role == Role.SYS:
            raise ValueError(
                f"{msg.role} not supported user-facing transcript Role, must be USR or AST"
            )
        self.__send('transcript ' + f"{msg.role.value} {msg.content}")

    async def start(self):
        if self.__tasks:
            self.logger.debug("Already started, no-op.")
            return
        self.logger.debug("Starting detector...")
        await self.detector.start()
        self.logger.info("Detector started!")
        task = asyncio.create_task(self.__run(), name="Main chat task")
        self.__tasks.append(task)

    async def stop(self):
        await self.detector.stop()
        self._send_status("disconnecting")
        for task in self.__tasks:
            task.cancel(f"{self.__class__.__name__}.stop() called")
        await asyncio.gather(*self.__tasks)
        self.__tasks = []

    async def wait_dc_connected(self):
        self.logger.debug("pc connected, awaiting dc...")
        await self.__dc_connected.wait()
        self.logger.debug("dc connected.")

    def add_dc(self, dc: RTCDataChannel):
        self.logger.debug("connecting dc to chatter")
        self.__dc = dc
        self.logger.success(f"dc connected: {dc.label}:{dc.id}")
        self.__dc_connected.set()

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

    async def __run(self):
        """Run the main program loop."""
        util.splash("moshi")
        await self.__dc_connected.wait()  # NOTE server handles timeout, TODO should be session controlling timeout
        self._send_status("hello")
        for i in itertools.count():
            if i == MAX_LOOPS and MAX_LOOPS != 0:
                self.logger.info(f"Reached MAX_LOOPS={MAX_LOOPS}, i={i}")
                self._send_status("done max conversation length reached")
                # TODO update client based on this message
                #     "Maximum conversation length reached."
                #     "\n\tThanks for using Moshi!\n\tPlease feel free to start a new conversation."
                # )
                break
            with logger.contextualize(i=i):
                self.logger.debug(f"starting loop")
            self._send_status("loopstart " + i)
            try:
                await self.__main()
            except UserResetError as e:
                self._send_error(str(e))  # TODO update client with \n\tPlease refresh the page
                break
            except MediaStreamError:
                logger.info("MediaStreamError, interpreting as a hangup, exiting.")
                break
        util.splash("bye")

    async def __main(self):
        """Run one loop of the main program.
        Raises:
            - UserResetError when chatter entered into a state that requires reset by user.
            - MediaStreamError when connection error or user hangup (disconnect).
        """
        try:
            usr_audio: AudioFrame = await self.__detect_user_utterance()
        except asyncio.TimeoutError as e:  # TODO should do timeout here?
            logger.error(f"Timed out getting user utterance: {e}")
            # TODO move this to client "Sorry, Moshi timed out waiting for your speech.\n\tWe'll try again!"
            self._send_error("utterance detection timeout")
            await asyncio.sleep(0.1)
            return  # skip to next loop
        self._send_status("transcribing")
        usr_text: str = await self.__transcribe_audio(usr_audio)
        usr_msg = self.__add_message(usr_text, Role.USR)
        self._send_transcript(usr_msg)
        await self.__init_character(sample_text=usr_text)
        self._send_status("thinking")
        ast_text: str = await self.__get_response()
        if ast_text:
            ast_msg = self.__add_message(ast_text, Role.AST)
            self._send_transcript(ast_msg)
            self._send_status("speaking")
            ast_audio: AudioFrame = await self.__synth_speech()
            await self.__send_assistant_utterance(ast_audio)
        else:
            self.logger.warning("Got empty assistant response")
            raise UserResetError("I have nothing to say.")

    async def __init_character(self, sample_text: str):
        """Using the sample text, initialize the voice and language used by Chatter."""
        if self.character is not None:
            return
        language = await lang.detect_language(sample_text)
        self.logger.debug(f"Language detected: {language}")
        voice = await speech.get_voice(language)
        self.logger.debug(f"Selected voice: {voice}")
        self.character = character.Character(voice, language)
        self.logger.info(f"Initialized character: {self.character}")

    async def __detect_user_utterance(self) -> AudioFrame:
        """
        Raises:
            - MediaStreamError
            - asyncio.TimeoutError
        """
        self.logger.debug("Detecting user utterance...")
        try:
            usr_audio: AudioFrame = await self.detector.get_utterance()
        except MediaStreamError:
            logger.debug("MediaStreamError: user disconnect while detecting utterance.")
            raise
        except asyncio.TimeoutError as e:
            logger.debug(f"Timed out waiting for user utterance: {e}")
            raise
        self.logger.info(f"Detected user utterance: {usr_audio}")
        return usr_audio

    async def __send_assistant_utterance(self, ast_audio: AudioFrame):
        self.logger.debug(f"Sending assistant utterance: {ast_audio}...")
        await self.responder.send_utterance(ast_audio)
        self.logger.info("Sent assistant utterance.")

    def __add_message(self, content: str, role: Role) -> Message:
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
