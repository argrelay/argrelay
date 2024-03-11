
Test command line with `TD_38_03_48_51`:

```sh
relay_demo goto host cm1 fs0 gr0 hs1 ro
```

The query with single collection for all `data_envelope`-s (of any `envelope_class`-es) -
`mongomock` returns an iterator which simply works constantly slow
(because of iterating through TD_38_03_48_51 large generated data set),
but returning only `data_envelope`-s matching the criteria.

Iteration 0: Baseline (unoptimized query)

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

Creating indexes for while using `mongomock` makes no difference
(understandably as mock is not supposed to address performance requirements).

Iteration 1: Create index for index fields with `mongomock`

```
...
0.000013s: [i=2]: before_try_iterate: DemoInterp
0.000268s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000020s: after_mongo_find
0.347675s: end_query_envelopes: dict_keys(['envelope_class']) 1000
0.000420s: [i=3]: before_consume_args: DemoInterp
0.000012s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000028s: after_mongo_find
0.339527s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity']) 100
0.000038s: begin_query_envelopes: ClassCluster
0.000002s: before_mongo_find
0.000027s: after_mongo_find
0.324278s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage']) 10
0.000023s: begin_query_envelopes: ClassCluster
0.000003s: before_mongo_find
0.000034s: after_mongo_find
0.324108s: end_query_envelopes: dict_keys(['envelope_class', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000012s: [i=3]: before_try_iterate: DemoInterp
0.000017s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000025s: after_mongo_find
0.336067s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name']) 10
0.000016s: [i=4]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassHost
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.325594s: end_query_envelopes: dict_keys(['envelope_class', 'cluster_name', 'host_name']) 1
0.000010s: [i=4]: before_try_iterate: DemoInterp
0.000010s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000026s: after_mongo_find
0.313632s: end_query_envelopes: dict_keys(['envelope_class']) 2
0.000011s: [i=5]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: access_type
0.000002s: before_mongo_find
0.000030s: after_mongo_find
0.317571s: end_query_envelopes: dict_keys(['envelope_class', 'access_type']) 1
...
3.621701s: total
```
