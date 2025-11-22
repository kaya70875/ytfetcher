import logging

def enable_default_config(level=logging.INFO):
    """
    Simple method for enabling basic logging.
    Args:
        level: Log level. Default to INFO
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )