# Structured logging setup using Python's built-in logging module.
import logging
import sys


def get_logger(name: str = "kyc_v2") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_event(logger: logging.Logger, level: str, message: str, **kwargs):
    extra = " | ".join(f"{key}={value}" for key, value in kwargs.items())

    log_message = f"{message} | {extra}" if extra else message

    if level.lower() == "info":
        logger.info(log_message)
    elif level.lower() == "warning":
        logger.warning(log_message)
    elif level.lower() == "error":
        logger.error(log_message)
    else:
        logger.debug(log_message)
