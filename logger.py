
import logging

# Create a logger for the package
logger = logging.getLogger("log_processor")

# Add NullHandler to prevent "No handlers could be found" warnings
# Applications using this package should configure their own handlers
logger.addHandler(logging.NullHandler())


def get_logger(name: str = "log_processor") -> logging.Logger:
    return logging.getLogger(name)


def setup_default_logging(
    level: int = logging.INFO,
    log_file: str | None = None,
    format_string: str = '%(levelname)s: %(message)s'
) -> None:
    """Configure logging with optional file output.

    Args:
        level: Logging level (default INFO)
        log_file: Path to log file. If None, console only.
        format_string: Log format string
    """
    formatter = logging.Formatter(format_string)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
