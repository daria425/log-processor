from profiler import Profiler
from logger import setup_default_logging
from streaming_processor import streaming_processor_v3
setup_default_logging(level=10)
file_path = "mock_logs.log"
profiler_instance = Profiler(streaming_processor_v3, file_path)
stats = profiler_instance.profile()
