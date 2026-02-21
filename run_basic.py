from profiler import Profiler
from basic_processor import basic_processor
import json
file_path = "mock_logs.log"
profiler_instance = Profiler(basic_processor, file_path)
stats = profiler_instance.profile()
with open("basic_processor_stats.json", "w") as f:
    json.dump(stats, f, indent=4)
