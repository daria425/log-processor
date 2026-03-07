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

cpdef parse_log_line_split(str line):
      cdef list parts = line.split(" - ", 4)
      if len(parts) != 5 or not parts[4].endswith("ms"):
          return None
      try:
          return LogEntry(
              timestamp=parts[0],
              method=parts[1],
              endpoint=parts[2],
              status_code=int(parts[3]),
              response_time_ms=int(parts[4][:-2])
          )
      except ValueError:
          return None


cpdef dict aggregate_lines(lines):
    """Aggregate log lines into stats in a single Cython loop.

    Args:
        lines: Iterator of raw log line strings

    Returns:
        Dict with total_logs, response_time_sum, status_codes_count, errors
    """
    cdef int total = 0
    cdef long response_time_sum = 0
    cdef int status_code, response_time
    cdef str line
    cdef list parts
    status_codes_count = {}

    for line in lines:
        parts = line.split(" - ", 4)
        if len(parts) == 5 and parts[4].endswith("ms"):
            try:
                status_code = int(parts[3])
                response_time = int(parts[4][:-2])
            except ValueError:
                continue
            total += 1
            response_time_sum += response_time
            if status_code not in status_codes_count:
                status_codes_count[status_code] = 0
            status_codes_count[status_code] += 1

    return {
        "total_logs": total,
        "response_time_sum": response_time_sum,
        "status_codes_count": status_codes_count,
    }