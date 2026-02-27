import re
import os
from dataclasses import dataclass, field

pattern = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+) - (\d{3}) - (\d+ms)')


@dataclass
class LogEntry:
    timestamp: str
    method: str
    endpoint: str
    status_code: int
    response_time_ms: int
    traceback: list = field(default_factory=list)


def parse_log_line_to_dict(line: str):
    try:
        timestamp_str, method, endpoint, status_code_str, response_time_str = line.strip().split(" - ")
        return {
            "timestamp": timestamp_str,
            "method": method,
            "endpoint": endpoint,
            "status_code": int(status_code_str),
            "response_time_ms": int(response_time_str.replace("ms", ""))
        }
    except ValueError:
        return None


def parse_log_line_regex(line):
    """
    Parse a log line using regex pattern matching and extract log entry components.
    
    Args:
        line (str): A single log line to be parsed.
    
    Returns:
        LogEntry: A LogEntry object containing parsed timestamp, method, endpoint, 
                  status_code, and response_time_ms if the line matches the pattern.
        None: If the line does not match the expected pattern.
    
    Raises:
        ValueError: If status_code_str or response_time_str cannot be converted to int.
    """
    match = pattern.match(line.strip())
    if match:
        timestamp_str, method, endpoint, status_code_str, response_time_str = match.groups()
        return LogEntry(
            timestamp=timestamp_str,
            method=method,
            endpoint=endpoint,
            status_code=int(status_code_str),
            response_time_ms=int(response_time_str)
        )
    return None


def process_chunk(chunk):
    pass


def get_chunk_boundaries(file_path: str, num_workers: int) -> list[tuple[int, int]]:
    """Split file into num_workers chunks aligned to line boundaries.

    Args:
        file_path: Path to the log file
        num_workers: Number of chunks to split into

    Returns:
        List of (start_byte, end_byte) tuples
    """
    file_size = os.path.getsize(file_path)
    chunk_size = file_size // num_workers
    boundaries = []

    with open(file_path, 'rb') as f:  # binary mode so seek/tell work on exact bytes
        for i in range(num_workers):
            start = i * chunk_size

            # align start to next newline (except for first chunk)
            if i != 0:
                f.seek(start)
                f.readline()       # read forward to next \n, discarding partial line
                start = f.tell()   # now we're at the start of a clean line

            # end of last chunk is always EOF
            if i == num_workers - 1:
                end = file_size
            else:
                f.seek((i + 1) * chunk_size)
                f.readline()       # same alignment for end
                end = f.tell()

            boundaries.append((start, end))

    return boundaries
