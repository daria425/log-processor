from utils import parse_log_line


def basic_processor(file_path: str):
    parsed_logs = []
    with open(file_path, 'r') as f:
        for log in f:
            parsed_log = parse_log_line(log)
            if parsed_log:
                parsed_logs.append(parsed_log)
    total_logs = len(parsed_logs)
    avg_response_time = sum(log['response_time_ms']
                            for log in parsed_logs) / total_logs
    status_codes_count = {}
    for log in parsed_logs:
        status_code = log['status_code']
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
    return {
        "total_logs": total_logs,
        "avg_response_time_ms": avg_response_time,
        "status_codes_count": status_codes_count
    }
