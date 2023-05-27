""" This module implements the core Chatter class that glues speech recognition, text to speech, and chat completion
capabilities together. """
from pprint import pformat

import pyfiglet
from loguru import logger

from moshimoshi import lang, listen, speak, think, util
from moshimoshi.base import Message, Role

logger.level("INSTRUCTION", no=38, color="<yellow><bold>")
logger.success("loaded")


class Chatter:
    """Main class for this app."""

    @util.timed
    def __init__(self):
        self.messages = [
            Message(
                Role.SYS,
                "Use elementary vocabulary to help a beginner learn a language.",
            )
        ]
        self.language = None
        self.iter = None

    @util.timed
    def _get_user_speech(self):
        """Get and transcribe the user's audible speech."""
        logger.log("INSTRUCTION", "SPEAK NOW")
        user_dialogue = listen.dialogue_from_mic()
        message = Message(Role.USR, user_dialogue)
        logger.debug(message)
        self.messages.append(message)

    @util.timed
    def _get_assistant_response(self):
        """Get the chat response from the LLM."""
        assistant_dialogue = think.completion_from_assistant(self.messages)
        message = Message(Role.AST, assistant_dialogue)
        logger.debug(message)
        self.messages.append(message)

    @util.timed
    def _say_assistant_response(self):
        """Play the assistant response text as audible language."""
        speak.say(self.assistant_utterance)

    @util.timed
    def _detect_language(self):
        """Detect the language the user is speaking."""
        if self.language:
            logger.debug(f"Language already detected: {self.language}")
            return
        self.language = lang.recognize_language(self.user_utterance)
        logger.debug(f"Language detected: {self.language}")

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

    def run(self):
        """This blocking function runs the core application loop."""
        self.iter = 1
        logger.log(
            "INSTRUCTION",
            "\n" + pyfiglet.Figlet(font="roman").renderText("moshi\nmoshi"),
        )
        while 1:
            logger.debug(f"iter: {self.iter}")
            self._get_user_speech()
            self._detect_language()
            self._get_assistant_response()
            self._say_assistant_response()
            self.iter = self.iter + 1
