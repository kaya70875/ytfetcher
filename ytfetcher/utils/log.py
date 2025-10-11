from typing import Literal
import colorama

LEVEL = Literal['INFO', 'WARNING', 'DONE', 'ERROR']

def decide_color(level: LEVEL):
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
    decided_color = decide_color(level=level)
    return print(decided_color + f'[{level}] ' + colorama.Style.RESET_ALL + message)