import logging

def setup_logging(verbose: bool = False):
    """
    Configure logging for CLI usage.

    Args:
        verbose: If True → DEBUG logs with full details.
                 If False → INFO logs with clean output.
    """
    level = logging.DEBUG if verbose else logging.INFO

    if verbose:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    else:
        fmt = "[%(levelname)s] %(message)s"

    logging.basicConfig(
        level=level,
        format=fmt,
    )