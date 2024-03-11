
Test command line with `TD_38_03_48_51`:

```sh
relay_demo goto host cm1 fs0 gr0 hs1 ro
```

This compares `mongomock` and `pymongo` handling 10 x times more data to see
if it scales linearly (O(n)) or better (e.g. O(log(n))).

Iteration 0-1: baseline Iteration 1 from `query_perf_mongomock_notes.md` (`mongomock` with indexes)

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

Iteration 0-2: baseline Iteration 3 from `query_perf_pymongo_notes.md` (`pymongo` with indexes)

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

Increasing data by 10 x times for `mongomock` increases query time roughly 10 x times as well
(2.923956s / 0.330452s ~ 8.85).

Iteration 1-1: Increase data x 10 times for `mongomock`

```
...
0.000013s: [i=2]: before_try_iterate: DemoInterp
0.000316s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000022s: after_mongo_find
2.923956s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000401s: [i=3]: before_consume_args: DemoInterp
0.000010s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000028s: after_mongo_find
2.852475s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000062s: begin_query_envelopes: ClassCluster
0.000004s: before_mongo_find
0.000031s: after_mongo_find
2.808685s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000019s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000029s: after_mongo_find
2.822847s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000012s: [i=3]: before_try_iterate: DemoInterp
0.000016s: begin_query_envelopes: ClassHost
0.000003s: before_mongo_find
0.000031s: after_mongo_find
2.921709s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000014s: [i=4]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassHost
0.000003s: before_mongo_find
0.000029s: after_mongo_find
2.847669s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000011s: [i=4]: before_try_iterate: DemoInterp
0.000011s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000027s: after_mongo_find
2.866389s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000012s: [i=5]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: access_type
0.000003s: before_mongo_find
0.000029s: after_mongo_find
...
31.751943s: total
```

Increasing data by 10 x times for `pymongo` increases query time roughly 5 x times
(0.066720s / 0.012577s ~ 5) and absolute number is still low.

Iteration 1-2: Increase data x 10 times for `pymongo`

```
...
0.000009s: [i=2]: before_try_iterate: DemoInterp
0.000218s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000014s: after_mongo_find
0.066720s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000011s: [i=3]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000025s: after_mongo_find
0.001709s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000010s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000017s: after_mongo_find
0.001862s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000019s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000027s: after_mongo_find
0.002469s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000014s: [i=3]: before_try_iterate: DemoInterp
0.000015s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.009211s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000010s: [i=4]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassHost
0.000003s: before_mongo_find
0.000025s: after_mongo_find
0.007547s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000014s: [i=4]: before_try_iterate: DemoInterp
0.000011s: begin_query_envelopes: access_type
0.000003s: before_mongo_find
0.000029s: after_mongo_find
0.000673s: end_query_envelopes: dict_keys(['envelope_class']) 2
...
0.093915s: total
```
