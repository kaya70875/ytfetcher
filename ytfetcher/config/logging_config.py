import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[37m',    # white
        'INFO': '\033[36m',     # cyan
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',    # red
        'CRITICAL': '\033[41m', # red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging(verbose: bool = False):
    """
    Configure logging for CLI usage.

    Args:
        verbose: If True → DEBUG logs with full details.
                 If False → INFO logs with clean output and colors.
    """
    level = logging.DEBUG if verbose else logging.INFO

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s" if verbose else "[%(levelname)s] %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(fmt))

    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True
    )