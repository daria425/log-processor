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
