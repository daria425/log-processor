from datetime import datetime
import random
from logger import setup_default_logging, get_logger
import time
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]
ENDPOINTS = ["/api/users", "/api/posts", "/api/resource", "/health"]

setup_default_logging()
logger = get_logger()


def log_line():
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {random.choice(METHODS)} - {random.choice(ENDPOINTS)} - {random.choice(STATUS_CODES)} - {random.randint(50, 200)}ms"


def init_log_file(file_path: str, num_lines: int = 500000):
    start_time = time.time()
    with open(file_path, 'w') as f:
        for i in range(num_lines):
            if i % 100000 == 0:
                logger.info(f"Generated {i} log lines...")
            f.write(log_line() + "\n")
        file_size = f.tell() / (1024 * 1024)  # Size in MB
    elapsed_time = time.time() - start_time
    logger.info(
        f"Finished generating {num_lines} log lines in {elapsed_time:.2f} seconds. Final file size: {file_size:.2f} MB")


if __name__ == "__main__":
    init_log_file("mock_logs.log")
