import re
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
