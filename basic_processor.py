from utils import parse_log_line_to_dict


def basic_processor(file_path: str):
    parsed_logs = []
    with open(file_path, 'r') as f:
        for log in f:
            parsed_log = parse_log_line_to_dict(log)
            if parsed_log:
                parsed_logs.append(parsed_log)
    total_logs = len(parsed_logs)
    response_time = 0
    status_codes_count = {}
    for log in parsed_logs:
        status_code = log['status_code']
        response_time += log['response_time_ms']
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
    avg_response_time = response_time / total_logs if total_logs > 0 else 0
    return {
        "total_logs": total_logs,
        "avg_response_time_ms": avg_response_time,
        "status_codes_count": status_codes_count
    }


if __name__ == "__main__":
    result = basic_processor("mock_logs.log")
    print(result)
