import os
from collections import defaultdict
from typing import Any
import logging
from logging.handlers import RotatingFileHandler

# Constants
LOG_TO_CONSOLE = False
LOGGING_COOLDOWN = 3
FORMAT = '{asctime} - [{levelname}] {filename}:{funcName}:{lineno} {name} - {message}'
INFO = logging.INFO
ERROR = logging.ERROR

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

class CooldownFilter(logging.Filter):
    """Do not print same line if time after previous line less or equal <COOLDOWN> seconds. Defaults to 5 seconds"""
    def __init__(self, name='', cooldown=5):
        """
        Initialize a filter.

        Initialize with the name of the logger which, together with its
        children, will have its events allowed through the filter. If no
        name is specified, allow every event.
        """
        self.name = name
        self.nlen = len(name)
        self.cooldown = cooldown
    
    last_events: dict[Any, float] = defaultdict(float)
    
    def filter(self, record):
        prev_time = self.last_events[record.lineno]
        if prev_time + self.cooldown <= record.created:
            self.last_events[record.lineno] = record.created
            return True
        else:
            return False


rotating_handler = RotatingFileHandler(
    filename=os.path.join(LOGS_DIR, "bot.log"),
    maxBytes=5 * 1024 * 1024,  
    backupCount=4, 
    encoding='utf-8'
)
rotating_handler.addFilter(CooldownFilter())
rotating_handler.setLevel(INFO)


streamHandler = logging.StreamHandler()
streamHandler.addFilter(CooldownFilter())
streamHandler.setLevel(INFO)


handlers = [rotating_handler, streamHandler] if LOG_TO_CONSOLE else [rotating_handler]


logging.basicConfig(
    format=FORMAT,
    level=INFO,
    style="{",
    handlers=handlers
)


logging.getLogger("aiogram").setLevel(INFO)
logging.getLogger("aiohttp").setLevel(INFO)