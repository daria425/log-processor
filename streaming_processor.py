import os
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
from parser import parse_log_line_regex
from logger import setup_default_logging
from utils import parse_log_line_to_dict, LogEntry, get_chunk_boundaries


def read_lines(file_path: str, boundaries: Optional[tuple[int, int]] = None):
    if boundaries:
        start, end = boundaries
        with open(file_path, "rb") as f:
            f.seek(start)
            while f.tell() < end:
                yield f.readline().decode("utf-8").rstrip("\n")
    else:
        with open(file_path) as f:
            for line in f:
                yield line.rstrip("\n")


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


def process_chunk(file_path: str, start: int, end: int, batch_size: int = 50) -> dict:
    """Process a single chunk of the log file, returning partial stats.

    Args:
        file_path: Path to the log file
        start: Start byte offset
        end: End byte offset
        batch_size: Number of errors per LLM batch

    Returns:
        Partial stats dict with response_time_sum (not avg) for correct merging
    """
    lines = read_lines(file_path, boundaries=(start, end))
    parsed = parse_lines_regex(lines)
    total = 0
    response_time_sum = 0
    status_codes_count = {}
    errors = []
    summaries = []
    for line in parsed:
        total += 1
        response_time_sum += line.response_time_ms
        status_code = line.status_code
        if status_code not in status_codes_count:
            status_codes_count[status_code] = 0
        status_codes_count[status_code] += 1
        if status_code not in [200, 201]:
            log_data = {
                "endpoint": line.endpoint,
                "status_code": line.status_code,
                "traceback": line.traceback[-1]
            }
            errors.append(log_data)
    return {
        "total_logs": total,
        # raw sum not avg - needed for correct merge
        "response_time_sum": response_time_sum,
        "status_codes_count": status_codes_count,
        "summaries": summaries,
        "errors": errors
    }


def streaming_processor(file_path: str, max_bytes: Optional[int] = None) -> dict:
    """Parallel streaming processor using ProcessPoolExecutor.

    Args:
        file_path: Path to the log file

    Returns:
        Merged stats from all workers
    """
    num_workers = os.cpu_count() // 2
    boundaries = get_chunk_boundaries(
        file_path, num_workers, max_bytes=max_bytes)

    with ProcessPoolExecutor(max_workers=num_workers, initializer=setup_default_logging, initargs=(logging.DEBUG,)) as executor:
        futures = [
            executor.submit(process_chunk, file_path, start, end, 10)
            for start, end in boundaries
        ]
        results = [f.result() for f in futures]

    total = sum(r["total_logs"] for r in results)
    response_time_sum = sum(r["response_time_sum"] for r in results)

    merged_status_counts = {}
    for r in results:
        for status_code, count in r["status_codes_count"].items():
            if status_code not in merged_status_counts:
                merged_status_counts[status_code] = 0
            merged_status_counts[status_code] += count
    all_errors = [e for r in results for e in r["errors"]]
    # llm call later
    return {
        "total_logs": total,
        "avg_response_time_ms": response_time_sum / total if total > 0 else 0,
        "status_codes_count": merged_status_counts,

    }
