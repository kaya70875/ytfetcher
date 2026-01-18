from ytfetcher.utils.state import RuntimeConfig
from typing import Literal
import colorama

LEVEL = Literal['INFO', 'WARNING', 'DONE', 'ERROR']

def decide_color(level: LEVEL):
    """
    Chooses color based on message level.
    Args:
        level(LEVEL): Message level.
    """
    match level:
        case 'INFO':
            return colorama.Fore.CYAN
        case 'WARNING':
            return colorama.Fore.YELLOW
        case 'ERROR':
            return colorama.Fore.RED
        case 'DONE':
            return colorama.Fore.GREEN

def log(message: str, level: LEVEL = ('INFO')):
    """
    Print message with different levels and colors. ex: (INFO, WARNING, DONE, ERROR).
    Args:
        message(str): The message to be printed.
        level(LEVEL): Priority level. Default to INFO
    """

    if not RuntimeConfig.is_verbose():
        return None

    decided_color = decide_color(level=level)
    return print(decided_color + f'[{level}] ' + colorama.Style.RESET_ALL + message)