# cli_utils.py

import logging
from pathlib import Path


def expand_user_paths(args, keys=("history", "alias", "log")):
    """Expands user directories in the specified argument keys."""
    for key in keys:
        if hasattr(args, key):
            setattr(args, key, str(Path(getattr(args, key)).expanduser()))
    return args


def configure_logger(log_path, level="DEBUG", name="repl_logger"):
    """Configures and returns a logger for the REPL session.

    Args:
        log_path: Path to the log file.
        level: Logging level (string or int).
        name: Logger name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.DEBUG))

    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
