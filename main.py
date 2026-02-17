from profiler import Profiler
from basic_processor import basic_processor
file_path = "mock_logs.log"
profiler_instance = Profiler(basic_processor, file_path)
stats = profiler_instance.profile()
print(stats)
