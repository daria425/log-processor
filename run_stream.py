from profiler import Profiler
from streaming_processor import streaming_processor
import json
file_path = "mock_logs.log"
profiler_instance = Profiler(streaming_processor, file_path)
stats = profiler_instance.profile()
with open("streaming_processor_stats.json", "w") as f:
    json.dump(stats, f, indent=4)
