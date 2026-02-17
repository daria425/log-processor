def parse_log_line(line: str):
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
