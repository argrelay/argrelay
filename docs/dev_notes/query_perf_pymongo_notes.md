
Test command line with `TD_38_03_48_51`:

```sh
relay_demo goto host cm1 fs0 gr0 hs1 ro
```

Note that the `total` row below in all snapshots is not sum of mearement captured in snapshots,
instead it is full end-to-end measurement (just FYI) for entire server request processing
(basically, some rows were excluded `...` from snapshots to arrive at the same `total` from snapshot data only).

Iteration 0: Baseline (unoptimized query) with `mongomock` before switching to `pymongo` (real MongoDB)

```
...
0.000012s: [i=2]: before_try_iterate: DemoInterp
0.000246s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000019s: after_mongo_find
0.330452s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000343s: [i=3]: before_consume_args: DemoInterp
0.000010s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000026s: after_mongo_find
0.304940s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000042s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.304607s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000016s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000026s: after_mongo_find
0.301533s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000011s: [i=3]: before_try_iterate: DemoInterp
0.000015s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000027s: after_mongo_find
0.336380s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000013s: [i=4]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.316279s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000011s: [i=4]: before_try_iterate: DemoInterp
0.000010s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.304807s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000010s: [i=5]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.305218s: end_query_envelopes: dict_keys(['envelope_class', 'access_type']) 1
...
3.410634s: total
```

Switching to `pymongo` (real MongoDB) even without indexes give x 6 boost in performance.

Iteration 1: Switch to  `pymongo` (real MongoDB)

```
...
0.000015s: [i=2]: before_try_iterate: DemoInterp
0.000276s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.055730s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000014s: [i=3]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000027s: after_mongo_find
0.054855s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000015s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000027s: after_mongo_find
0.052194s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000014s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000026s: after_mongo_find
0.053017s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000013s: [i=3]: before_try_iterate: DemoInterp
0.000015s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.051352s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000010s: [i=4]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.051846s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000012s: [i=4]: before_try_iterate: DemoInterp
0.000009s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.046119s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000011s: [i=5]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.052434s: end_query_envelopes: dict_keys(['envelope_class', 'access_type']) 1
...
0.577934s: total
```

Searching envelopes by indexed fields becomes extra x 20 faster.

For non-indexed fields (like `envelope_class` which was simply forgotten), the search remains roughly the same.

Iteration 2: Create index for index fields with `pymongo` (real MongoDB)

```
...
0.000015s: [i=2]: before_try_iterate: DemoInterp
0.000251s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000023s: after_mongo_find
0.055623s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000012s: [i=3]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.002147s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000012s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000021s: after_mongo_find
0.001927s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000011s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000018s: after_mongo_find
0.002384s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000019s: [i=3]: before_try_iterate: DemoInterp
0.000021s: begin_query_envelopes: ClassHost
0.000004s: before_mongo_find
0.000035s: after_mongo_find
0.002347s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000011s: [i=4]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassHost
0.000003s: before_mongo_find
0.000026s: after_mongo_find
0.002310s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000012s: [i=4]: before_try_iterate: DemoInterp
0.000036s: begin_query_envelopes: access_type
0.000016s: before_mongo_find
0.000027s: after_mongo_find
0.049016s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000010s: [i=5]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.001322s: end_query_envelopes: dict_keys(['envelope_class', 'access_type']) 1
...
0.040172s: total
```

Search for using `envelope_class` field is reduced by 0.055623 / 0.012577 = x 4+ times.

Iteration 3: Create index for all fields participating in any query with `pymongo` (real MongoDB)

```
...
0.000024s: [i=2]: before_try_iterate: DemoInterp
0.000391s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000030s: after_mongo_find
0.012577s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000018s: [i=3]: before_consume_args: DemoInterp
0.000010s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000028s: after_mongo_find
0.002606s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000022s: begin_query_envelopes: ClassCluster
0.000004s: before_mongo_find
0.000037s: after_mongo_find
0.002961s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000021s: begin_query_envelopes: ClassCluster
0.000005s: before_mongo_find
0.000030s: after_mongo_find
0.003145s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000019s: [i=3]: before_try_iterate: DemoInterp
0.000021s: begin_query_envelopes: ClassHost
0.000003s: before_mongo_find
0.000037s: after_mongo_find
0.001918s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000011s: [i=4]: before_consume_args: DemoInterp
0.000010s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000027s: after_mongo_find
0.009308s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000013s: [i=4]: before_try_iterate: DemoInterp
0.000010s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.000667s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000009s: [i=5]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000029s: after_mongo_find
0.000651s: end_query_envelopes: dict_keys(['envelope_class', 'access_type']) 1
...
0.040172s: total
```
