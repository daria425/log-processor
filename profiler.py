import tracemalloc
from dataclasses import asdict
import cProfile
import pstats
from typing import Callable
import time


class Profiler:
    def __init__(self, func: Callable, file_path: str):
        self.func = func
        self.file_path = file_path

    def get_true_time(self, *args, **kwargs):
        start_time = time.perf_counter()
        self.func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        return elapsed_time

    def profile(self):

        profiler = cProfile.Profile()
        profiler.enable()
        tracemalloc.start()
        start_time = time.perf_counter()
        self.func(self.file_path)
        elapsed_time = time.perf_counter() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        # return stats.get_stats_profile().func_profiles
        return {
            "peak_memory_usage_mb": peak / (1024 * 1024),
            "cumulative_time": stats.total_tt,
            "true_elapsed_time": elapsed_time,
            "function_profiles": {
                key: asdict(value) for key, value in stats.get_stats_profile().func_profiles.items()
            }
        }


if __name__ == "__main__":
    from streaming_processor import streaming_processor_v1
    file_path = "mock_logs.log"
    profiler_instance = Profiler(streaming_processor_v1, file_path)
    time = profiler_instance.get_true_time(profiler_instance.file_path)
    print(f"True execution time: {time:.4f} seconds")
