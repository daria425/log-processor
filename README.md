# log-processor

A Python exploration into processing large line-delimited files (web server logs, JSONL, etc.) as efficiently as possible. The core idea is a streaming pipeline that reads line by line, keeping memory usage constant regardless of file size, benchmarked against a naive baseline that loads everything into memory (see [performance stats](./performance_stats)).
The longer term goal is for this to serve as the backbone of an AI agent that streams, filters, and summarises logs, sending only relevant errors to an LLM rather than a whole file that would blow any context window.

## Benchmark summary

`basic_processor` was only profiled on ~90MB of log data; it ran out of memory at 1GB, so it is excluded from the streaming comparison table.

Speedup is computed as `v1_time / run_time` (so values `> 1x` are faster than v1). Memory reduction is computed as `1 - run_peak_memory / v1_peak_memory` (negative values mean higher memory usage than v1).

| Run                                     | Stats file                                 | Peak memory (MB) | Cumulative time (s) | Speedup vs v1 | Memory reduction vs v1 |
| --------------------------------------- | ------------------------------------------ | ---------------: | ------------------: | ------------: | ---------------------: |
| Streaming v1 (baseline)                 | `streaming_processor_stats_v1.json`        |         0.027815 |          474.237243 |         1.00x |                  0.00% |
| Streaming v2 (regex)                    | `streaming_processor_stats_v2.json`        |         0.024434 |          249.935471 |         1.90x |                 12.16% |
| Streaming v2 (regex + Cython)           | `streaming_processor_stats_v2_cython.json` |         0.023916 |          345.551013 |         1.37x |                 14.01% |
| Streaming v3 (multiprocessing)          | `streaming_processor_stats_v3.json`        |         0.231326 |          119.271588 |         3.98x |               -731.72% |
| Streaming v3 (multiprocessing + Cython) | `streaming_processor_stats_v3_cython.json` |         0.230999 |           90.896777 |         5.22x |               -730.54% |
