from profiler import Profiler
from streaming_processor import streaming_processor_v2
import json
file_path = "mock_logs.log"
profiler_instance = Profiler(streaming_processor_v2, file_path)
stats = profiler_instance.profile()
with open("performance_stats/streaming_processor_stats_v2.json", "w") as f:
    json.dump(stats, f, indent=4)
