""" This module implements the core Chatter class that glues speech recognition, text to speech, and chat completion
capabilities together. """
from loguru import logger

from moshimoshi import conversation, text2speech, speech2text

class Chatter:
    def __init__(self):
        self.messages = [
        ]
        self.language = None

    def run(self):
        """ Runs the main chat loop: stt->nlp->tts """
        while 1:
            logger.debug("Getting user_dialogue...")
            user_dialogue: str = speech2text.listen()
            logger.debug(f"Got user_dialogue:\n'''\n{user_dialogue}\n'''")
            logger.transcript(f'user:\n{user_dialogue}')
            assert isinstance(user_dialogue, str)
            logger.debug("Getting ai_dialogue...")
            response: conversation.Response = conversation.respond(user_dialogue)
            ai_dialogue: str = response.chat_completion
            language: str = response.language
            logger.debug(f"Got ai_dialogue:\n{ai_dialogue}")
            logger.debug(f"Recognized language: {language}")
            logger.transcript(f'assistant:\n{ai_dialogue}')
            assert isinstance(ai_dialogue, str)
            logger.debug("Saying...")
            text2speech.say(ai_dialogue, language)
            logger.debug("Said!")
            logger.warning("Quitting after one loop for development purposes...")
            # TODO add the user and ai dialogue to the prompt
            break
        logger.info('Done chatting!')
