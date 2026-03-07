from profiler import Profiler
from logger import setup_default_logging
from streaming_processor import streaming_processor
import json
setup_default_logging(level=10)
file_path = "mock_logs.log"
profiler_instance = Profiler(streaming_processor, file_path)
stats = profiler_instance.profile()
with open("performance_stats/streaming_processor_stats_v5.json", "w") as f:
    json.dump(stats, f, indent=4)
