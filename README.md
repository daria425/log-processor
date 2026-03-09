# log-processor

## Overview

A Python exploration into processing large line-delimited files (web server logs, JSONL, etc.) as efficiently as possible.

The project began as a streaming log processor focused on high throughput parsing while keeping memory usage constant regardless of file size. The core design reads logs line by line rather than loading the entire dataset into memory, and is benchmarked against a naive baseline that loads everything at once.

The system currently processes a synthetic dataset of tens of millions of log lines in a few seconds on a single machine.

The next step is building a lightweight query layer over the parsed events so that logs can be filtered, aggregated, and explored programmatically. Over time the project will evolve into a small observability style engine capable of detecting and summarising operational signals from raw logs.

## Motivation

Most log analysis tools either:

- load large files directly into memory
- rely on heavy external systems
- or send entire logs to LLMs for analysis

This project explores a different approach.

The goal is to turn raw log streams into structured signals first, then use those signals to decide what information is actually worth sending to a language model.

Instead of giving an LLM gigabytes of logs that would exceed any context window, the system aims to stream, filter, and summarise logs so that only the relevant portions reach the model.

## Current focus

- High throughput parsing of large line-delimited log files
- Streaming pipeline with constant memory usage
- Benchmarks against naive in-memory approaches
- Structured event extraction from raw logs

## Next steps

- Lightweight query engine over structured events
- Fast filtering by service, level, and time window
- Aggregations such as top error patterns or service level summaries
- Detection of suspicious time windows or error spikes

## Long term direction

The long term goal is to use the pipeline as the backbone of an AI assisted incident analysis tool.

Logs will be streamed and reduced into structured summaries before any interaction with a language model. The model then receives a condensed view of the relevant signals rather than the entire log corpus.

This keeps token usage low while still allowing automated diagnosis or summarisation of system behaviour.

## Benchmark summary

`basic_processor` was only profiled on ~90MB of log data; it ran out of memory at 1GB, so it is excluded from the streaming comparison table.

Speedup is computed as `v1_time / run_time` (so values `> 1x` are faster than v1). Memory reduction is computed as `1 - run_peak_memory / v1_peak_memory` (negative values mean higher memory usage than v1).

| Run                                             | Stats file                                      | Peak memory (MB) | Cumulative time (s) | Speedup vs v1 | Memory reduction vs v1 |
| ----------------------------------------------- | ----------------------------------------------- | ---------------: | ------------------: | ------------: | ---------------------: |
| Streaming v1 (baseline)                         | `streaming_processor_stats_v1.json`             |         0.027815 |          474.237243 |         1.00x |                  0.00% |
| Streaming v2 (regex)                            | `streaming_processor_stats_v2.json`             |         0.024434 |          249.935471 |         1.90x |                 12.16% |
| Streaming v2 (regex + Cython)                   | `streaming_processor_stats_v2_cython.json`      |         0.023916 |          345.551013 |         1.37x |                 14.01% |
| Streaming v3 (multiprocessing)                  | `streaming_processor_stats_v3.json`             |         0.231326 |          119.271588 |         3.98x |               -731.72% |
| Streaming v3 (multiprocessing + Cython)         | `streaming_processor_stats_v3_cython.json`      |         0.230999 |           90.896777 |         5.22x |               -730.54% |
| Streaming final baseline (lightweight profiler) | `streaming_processor_stats_final_baseline.json` |         0.060095 |            3.900993 |       121.57x |               -116.06% |

For the final baseline run, profiling switched from `cProfile` to a lightweight two-pass method to avoid profiler overhead and `tracemalloc` fork inheritance effects:

```python
def profile_lightweight(self, *args, **kwargs):
	"""Time + memory separately to avoid tracemalloc fork inheritance."""
	# timing pass - no tracemalloc
	start = time.perf_counter()
	self.func(self.file_path, *args, **kwargs)
	elapsed = time.perf_counter() - start

	# memory pass - small slice only
	tracemalloc.start()
	self.func(self.file_path, max_bytes=50 * 1024 * 1024, *args, **kwargs)
	_, peak = tracemalloc.get_traced_memory()
	tracemalloc.stop()

	return {
		"true_elapsed_time": elapsed,
		"peak_memory_usage_mb": peak / (1024 * 1024),
	}
```
