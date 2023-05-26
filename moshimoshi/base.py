""" This module provides base types used in various app functions. """
from dataclasses import dataclass
from enum import Enum

from loguru import logger

logger.success("loaded")

class Role(str, Enum):
    SYS = "system"
    USR = "user"
    AST = "assistant"

@dataclass
class Message:
    # NOTE .asdict()
    role: Role
    content: str
