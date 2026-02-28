from profiler import Profiler
from streaming_processor import streaming_processor_v3
import json
file_path = "mock_logs.log"
profiler_instance = Profiler(streaming_processor_v3, file_path)
stats = profiler_instance.profile()
with open("performance_stats/streaming_processor_stats_v3_cython.json", "w") as f:
    json.dump(stats, f, indent=4)
