import tracemalloc
from dataclasses import asdict
import cProfile
import pstats
from typing import Callable


class Profiler:
    def __init__(self, func: Callable, file_path: str):
        self.func = func
        self.file_path = file_path

    def profile(self):
        profiler = cProfile.Profile()
        profiler.enable()
        tracemalloc.start()
        self.func(self.file_path)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        # return stats.get_stats_profile().func_profiles
        return {
            "peak_memory_usage_mb": peak / (1024 * 1024),
            "cumulative_time": stats.total_tt,
            "function_profiles": {
                key: asdict(value) for key, value in stats.get_stats_profile().func_profiles.items()
            }
        }
