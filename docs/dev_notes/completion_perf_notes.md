
These are notes on optimization done for end-to-end request-response specifically for Tab-completion.

# Scope

The server-side query execution is factored out from this doc - here:
*    the focus is on data round-trip
*    all tests use the same (small) data set

For server-side query optimization with different data set sizes see instead:
*   `DistinctValuesQuery`
*   `test_QueryEngine_perf.py`

# Results ahead of details

The biggest perf impact is contributed by `import`-s<br/>
(even choice of HTTP-client is driven by time to `import` specific library).

This suggests that server lookup is hardly embeddable (to make `argrelay` serverless),<br/>
unless using custom data-crunching logic with minimum `import`-s (or even not in Python).

# Why bother optimizing?

Unlike many GUI-s, Bash CLI does not have async execution -
Tab-completion request blocks shell completely.  

*   For humans, end-to-end request-response better be under 200 millis.
*   It is hardly noticeable if under 50 millis.
*   With optimization below it was brought down from 200+ to 20- millis.

# How to do it?

At the time of writing, exporting `ARGRELAY_DEBUG` env var made
measurements collected via `ElapsedTime.measure` printed in `stdout` on each request-response.

To keep comparison apple-to-apple, the performance measurements were done on the same machine.

The numbers are approximate - whatever seem to show up most of the time.

# Trying optimized and non-optimized command for `ServerAction.ProposeArgValues`

There are two implementations for `ServerAction.ProposeArgValues`:
*   `ProposeArgValuesRemoteOptimizedClientCommand`
*   `ProposeArgValuesRemoteClientCommand`

It is possible to select between the two by setting `ClientConfig.optimize_completion_request` to true or false.

Roughly their round-trip is respectively `20 ms` and `120 ms`.

# Optimizing Tab-completion client request-response

Table below goes through optimization iterations:
*   Iteration 0: non-optimized version (still in use for commands `ServerAction.DescribeLineArgs` or `ServerAction.RelayLineArgs`).
*   Iteration 4: optimized version for `ServerAction.ProposeArgValues`.

All numbers are deltas between prev and curr marks except end-to-end `total` mark (a delta between first and last).

| `ElapsedTime` mark            | Iteration 0 | Iteration 1 | Iteration 2 | Iteration 3 | Iteration 4 |
|-------------------------------|-------------|-------------|-------------|-------------|-------------|
| `after_program_entry`         | 0.000000s   | 0.000000s   | 0.000000s   | 0.000000s   | 0.000000s   |
| `after_initial_imports`       | 0.043226s   | 0.047991s   | 0.047752s   | 0.005449s   | 0.005476s   |
| `after_loading_client_config` | 0.000933s   | 0.000989s   | 0.001028s   | 0.000107s   | 0.000107s   |
| `before_client_invocation`    | 0.150371s   | 0.000868s   | 0.000896s   | 0.001079s   | 0.001104s   |
| `before_request`              | 0.000151s   | 0.063905s   | 0.008411s   | 0.020431s   | 0.004538s   |
| `after_request`               | 0.006135s   | 0.006064s   | 0.004829s   | 0.004675s   | 0.003307s   |
| `after_deserialization`       | 0.000025s   | 0.000021s   | 0.000089s   | 0.000067s   | 0.000010s   |
| `after_request_processed`     | 0.000007s   | 0.000006s   | 0.000014s   | 0.000012s   | 0.000092s   |
| `on_exit`                     | 0.000002s   | 0.000001s   | 0.000002s   | 0.000002s   | 0.000004s   |
| ----------------------------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| `total`                       | 0.200850s   | 0.119845s   | 0.063021s   | 0.031822s   | 0.014637s   |

What was done in each iteration:
*   Iteration 0: Baseline (what is typical for other non-optimized commands).
*   Iteration 1: Make imports conditional (import only when needed).
*   Iteration 2: Switch from `requests` to `http.client`.
*   Iteration 3: Do not import `Schema`-s for Tab-completion and use `*.json` config instead of `*.yaml`.
*   Iteration 4: Switch from `http.client` to plain `socket`.

# Choice of client config format

The load time difference between client configs in `*.json` or `*.py` is hardly noticeable,
therefore, `*.json` was chosen as a more conventional config format.

| Config format | Time to load config | End-to-end time | Pros                            | Cons                               |
|---------------|---------------------|-----------------|---------------------------------|------------------------------------|
| `*.py`        | 5 millis            | 12 millis       | Fastest.                        | But prog lang is weird for config. |
| `*.json`      | 7 millis            | 14 millis       | Fast and still a config format. | Not uniform with server config.    |
| `*.yaml`      | 19 millis           | 26 millis       | Uniform with server config.     | Why loosing 12 millis to `*.json`? |

# See also

Module imports done by `ProposeArgValuesRemoteOptimizedClientCommand` are constrained by this test:

```
tests/offline_tests/relay_client/test_ProposeArgValuesRemoteOptimizedClientCommand.py
```

# Raw data

This is already summarized in one of the tables above:

```
Iteration 0: Baseline (what is typical for other non-optimized commands):
0.000000s: after_program_entry
0.043226s: after_initial_imports
0.000933s: after_loading_client_config
0.150371s: before_client_invocation
0.000151s: before_request
0.006135s: after_request
0.000025s: after_deserialization
0.000007s: after_request_processed
0.000002s: on_exit
0.200850s: total

Iteration 1: Make imports conditional (import only when needed):
0.000000s: after_program_entry
0.047991s: after_initial_imports
0.000989s: after_loading_client_config
0.000868s: before_client_invocation
0.063905s: before_request
0.006064s: after_request
0.000021s: after_deserialization
0.000006s: after_request_processed
0.000001s: on_exit
0.119845s: total

Iteration 2: Switch from `requests` to `http.client`:
0.000000s: after_program_entry
0.047752s: after_initial_imports
0.001028s: after_loading_client_config
0.000896s: before_client_invocation
0.008411s: before_request
0.004829s: after_request
0.000089s: after_deserialization
0.000014s: after_request_processed
0.000002s: on_exit
0.063021s: total

Iteration 3: Do not import `Schema`-s for Tab-completion and use `*.json` config instead of `*.yaml`:
0.000000s: after_program_entry
0.005449s: after_initial_imports
0.000107s: after_loading_client_config
0.001079s: before_client_invocation
0.020431s: before_request
0.004675s: after_request
0.000067s: after_deserialization
0.000012s: after_request_processed
0.000002s: on_exit
0.031822s: total

Iteration 4: Switch from `http.client` to plain `socket`:
0.000000s: after_program_entry
0.005476s: after_initial_imports
0.000107s: after_loading_client_config
0.001104s: before_client_invocation
0.004538s: before_request
0.003307s: after_request
0.000010s: after_deserialization
0.000092s: after_request_processed
0.000004s: on_exit
0.014637s: total
```
