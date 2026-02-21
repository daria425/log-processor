from datetime import datetime
import random
import os
from logger import setup_default_logging, get_logger
from logging import Logger

ENDPOINTS = ["/api/v1/resource", "/api/v1/users", "/api/v1/items"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]


def generate_line():
    timestamp = datetime.now().isoformat()
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status_code = random.choice(STATUS_CODES)
    response_time = random.randint(10, 5000)  # ms
    return f"{timestamp} - {method} - {endpoint} - {status_code} - {response_time}ms\n"


def make_logs(log_file_size=8_000_000, file_path: str = "mock_logs.log", logger_instance: Logger = None):  # approx 500mb
    with open(file_path, "w") as f:
        for _ in range(log_file_size):
            f.write(generate_line())
    file_size = os.path.getsize(file_path)
    if logger_instance:
        logger_instance.info(
            f"Generated log file of size: {file_size / (1024 * 1024):.2f} MB at {file_path}")


if __name__ == "__main__":
    logger = get_logger()
    setup_default_logging()
    make_logs(logger_instance=logger)
