import os
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
from parser import aggregate_lines
import time
from logger import setup_default_logging
from utils import get_chunk_boundaries


def read_lines(file_path: str, boundaries: Optional[tuple[int, int]], buffer_size: int = 1024 * 1024):
    start, end = boundaries
    with open(file_path, "rb") as f:
        f.seek(start)
        remainder = b""
        while f.tell() < end:
            to_read = min(buffer_size, end - f.tell())
            chunk = f.read(to_read)
            if not chunk:
                break
            lines = (remainder + chunk).split(b"\n")
            remainder = lines.pop()  # last line may be incomplete
            for line in lines:
                # bottleneck:  iterator protocol (a __next__ call + exception check) on every single line
                yield line.decode("utf-8")
        if remainder:
            yield remainder.decode("utf-8")


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
    return aggregate_lines(lines)


def profile_worker(file_path: str, start: int, end: int, batch_size: int = 50):
    t0 = time.perf_counter()
    lines = read_lines(file_path, boundaries=(start, end))
    result = aggregate_lines(lines)
    print(f"aggregate_lines: {time.perf_counter() - t0:.2f}s")
    return result


def profile_worker_read_time(file_path: str, start: int, end: int, batch_size: int = 50):
    t0 = time.perf_counter()
    for _ in read_lines(file_path, boundaries=(start, end)):
        pass
    t1 = time.perf_counter()
    lines = read_lines(file_path, boundaries=(start, end))
    result = aggregate_lines(lines)
    t2 = time.perf_counter()
    print(f"read: {t1 - t0:.2f}s | parse: {t2 - t1:.2f}s")
    return result


def streaming_processor(file_path: str, max_bytes: Optional[int] = None) -> dict:
    """Parallel streaming processor using ProcessPoolExecutor.

    Args:
        file_path: Path to the log file

    Returns:
        Merged stats from all workers
    """
    num_workers = max(4, os.cpu_count() // 2)
    boundaries = get_chunk_boundaries(
        file_path, num_workers, max_bytes=max_bytes)

    with ProcessPoolExecutor(max_workers=num_workers, initializer=setup_default_logging, initargs=(logging.DEBUG,)) as executor:
        futures = [
            executor.submit(process_chunk,
                            file_path, start, end, 10)
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
    # all_errors = [e for r in results for e in r["errors"]]
    # llm call later
    return {
        "total_logs": total,
        "avg_response_time_ms": response_time_sum / total if total > 0 else 0,
        "status_codes_count": merged_status_counts,

    }
