from utils import pattern, LogEntry


cpdef parse_log_line_regex(str line):
    cdef str timestamp, method, endpoint, status_code_str, response_time_str
    match = pattern.match(line.strip())
    if match:
        timestamp_str, method, endpoint, status_code_str, response_time_str = match.groups()
        return LogEntry(
            timestamp=timestamp_str,
            method=method,
            endpoint=endpoint,
            status_code=int(status_code_str),
            response_time_ms=int(response_time_str.replace("ms", ""))
        )
    return None