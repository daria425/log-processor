
from logger import setup_default_logging
from streaming_processor import streaming_processor
setup_default_logging(level=10)
file_path = "mock_logs.log"
logs_analysis_result = streaming_processor(
    file_path, max_bytes=10 * 1024 * 1024)  # Process first 10MB of the log file
