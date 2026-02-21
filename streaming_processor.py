from utils import parse_log_line


def read_lines(file_path: str):
    with open(file_path) as f:
        for line in f:
            yield line.strip()


def parse_lines(lines):
    for line in lines:
        parsed = parse_log_line(line)
        if parsed:
            yield parsed


def streaming_processor(file_path: str):
    lines = read_lines(file_path)
    parsed = parse_lines(lines)
    total = 0
    response_time_sum = 0
    status_codes_count = {}
    for line in parsed:
        total += 1
        response_time_sum += line['response_time_ms']
        status_code = line["status_code"]
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
    avg_response_time = response_time_sum / total if total > 0 else 0
    return {
        "total_logs": total,
        "avg_response_time_ms": avg_response_time,
        "status_codes_count": status_codes_count
    }
    # do shit
