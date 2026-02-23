from utils import parse_log_line_to_dict, parse_log_line_regex, LogEntry
from nodes.logs_analysis import send_log_batch
from logger import logger


def read_lines(file_path: str):
    with open(file_path) as f:
        for line in f:
            yield line.strip()


def parse_lines_to_dict(lines):
    current_entry: dict | None = None
    for line in lines:
        if len(line.split(" - ")) == 5:
            if current_entry:
                yield current_entry
            current_entry = parse_log_line_to_dict(line)
            if current_entry:
                current_entry["traceback"] = []
        else:
            if current_entry:
                current_entry["traceback"].append(line.strip())
    if current_entry:
        yield current_entry


def parse_lines_regex(lines):
    current_entry: LogEntry | None = None
    for line in lines:
        parsed = parse_log_line_regex(line)
        if parsed:
            if current_entry:
                yield current_entry
            current_entry = parsed
        else:
            if current_entry:
                current_entry.traceback.append(line.strip())
    if current_entry:
        yield current_entry


def streaming_processor_v1(file_path: str, batch_size: int = 50):  # start w 50
    lines = read_lines(file_path)
    parsed = parse_lines_to_dict(lines)
    total = 0
    response_time_sum = 0
    status_codes_count = {}
    errors = []
    for line in parsed:
        total += 1
        response_time_sum += line['response_time_ms']
        status_code = line["status_code"]
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
        if status_code not in [200, 201]:
            log_data = {
                ** line,
                "traceback": "\n".join(line.get("traceback", []))
            }
            errors.append(log_data)
            if len(errors) >= batch_size:
                logger.info("Sending batch to llm")
                sample = errors[0]
                logger.debug(f"Sample log for LLM: {sample}")
                summary = send_log_batch(errors)
                errors.clear()  # flush
    avg_response_time = response_time_sum / total if total > 0 else 0
    return {
        "total_logs": total,
        "avg_response_time_ms": avg_response_time,
        "status_codes_count": status_codes_count
    }


def streaming_processor_v2(file_path: str, batch_size: int = 50):  # start w 50
    lines = read_lines(file_path)
    parsed = parse_lines_regex(lines)
    total = 0
    response_time_sum = 0
    status_codes_count = {}
    errors = []
    for line in parsed:
        total += 1
        response_time_sum += line.response_time_ms
        status_code = line.status_code
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
        if status_code not in [200, 201]:
            log_data = {
                "timestamp": line.timestamp,
                "method": line.method,
                "endpoint": line.endpoint,
                "status_code": line.status_code,
                "response_time_ms": line.response_time_ms,
                "traceback": "\n".join(line.traceback)
            }
            errors.append(log_data)
            if len(errors) >= batch_size:
                logger.info("Sending batch to llm")
                sample = errors[0]
                logger.debug(f"Sample log for LLM: {sample}")
                summary = send_log_batch(errors)
                errors.clear()  # flush
    avg_response_time = response_time_sum / total if total > 0 else 0
    return {
        "total_logs": total,
        "avg_response_time_ms": avg_response_time,
        "status_codes_count": status_codes_count
    }
