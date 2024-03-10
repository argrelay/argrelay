
# Results ahead of details

| without cache | with cache |
|---------------|------------|
| 2.734048s     | 0.001324s  |

The biggest contributor (when cache is disabled) is actually query results processing (which is also cached).

# Detailed output

The query was against `mongomock`
(this does not matter as it returns immediately, traversing results takes time).

Tested with `TD_38_03_48_51` and this command line:

```sh
relay_demo goto host cm1 fs3 gr5 hs7 rw |
```

1st Tab:

```
0.000000s: before_request_payload_load
0.000732s: after_input_context_creation
0.000140s: [i=1]: before_consume_args: FirstArgInterp
0.000009s: [i=1]: before_try_iterate: FirstArgInterp
0.000004s: [i=1]: before_contribute_to_completion: FirstArgInterp
0.000002s: [i=1]: after_contribute_to_completion: FirstArgInterp
0.000115s: begin_query_envelopes: ClassFunction
0.000005s: before_cache_lookup
0.000039s: after_cache_lookup
0.000001s: before_mongo_find
0.000020s: after_mongo_find
0.251337s: end_query_envelopes: dict_keys(['EnvelopeClass']) 5
0.000006s: [i=2]: before_consume_args: DemoInterp
0.000014s: begin_query_envelopes: ClassFunction
0.000006s: before_cache_lookup
0.000025s: after_cache_lookup
0.000001s: before_mongo_find
0.000024s: after_mongo_find
0.240743s: end_query_envelopes: dict_keys(['EnvelopeClass', 'ActionType']) 2
0.000010s: begin_query_envelopes: ClassFunction
0.000006s: before_cache_lookup
0.000027s: after_cache_lookup
0.000001s: before_mongo_find
0.000023s: after_mongo_find
0.253123s: end_query_envelopes: dict_keys(['EnvelopeClass', 'ActionType', 'ObjectSelector']) 1
0.000010s: [i=2]: before_try_iterate: DemoInterp
0.000295s: begin_query_envelopes: ClassCluster
0.000004s: before_cache_lookup
0.000026s: after_cache_lookup
0.000001s: before_mongo_find
0.000018s: after_mongo_find
0.268530s: end_query_envelopes: dict_keys(['EnvelopeClass']) 1000
0.000008s: [i=3]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassCluster
0.000007s: before_cache_lookup
0.000036s: after_cache_lookup
0.000001s: before_mongo_find
0.000022s: after_mongo_find
0.247683s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity']) 100
0.000010s: begin_query_envelopes: ClassCluster
0.000006s: before_cache_lookup
0.000027s: after_cache_lookup
0.000001s: before_mongo_find
0.000023s: after_mongo_find
0.238283s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity', 'flow_stage']) 10
0.000010s: begin_query_envelopes: ClassCluster
0.000007s: before_cache_lookup
0.000028s: after_cache_lookup
0.000001s: before_mongo_find
0.000025s: after_mongo_find
0.239986s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000009s: [i=3]: before_try_iterate: DemoInterp
0.000021s: begin_query_envelopes: ClassHost
0.000004s: before_cache_lookup
0.000027s: after_cache_lookup
0.000001s: before_mongo_find
0.000024s: after_mongo_find
0.251899s: end_query_envelopes: dict_keys(['EnvelopeClass', 'cluster_name']) 10
0.000007s: [i=4]: before_consume_args: DemoInterp
0.000009s: begin_query_envelopes: ClassHost
0.000006s: before_cache_lookup
0.000027s: after_cache_lookup
0.000001s: before_mongo_find
0.000023s: after_mongo_find
0.247702s: end_query_envelopes: dict_keys(['EnvelopeClass', 'cluster_name', 'host_name']) 1
0.000008s: [i=4]: before_try_iterate: DemoInterp
0.000023s: begin_query_envelopes: access_type
0.000004s: before_cache_lookup
0.000032s: after_cache_lookup
0.000001s: before_mongo_find
0.000026s: after_mongo_find
0.250506s: end_query_envelopes: dict_keys(['EnvelopeClass']) 2
0.000007s: [i=5]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: access_type
0.000006s: before_cache_lookup
0.000027s: after_cache_lookup
0.000001s: before_mongo_find
0.000023s: after_mongo_find
0.242053s: end_query_envelopes: dict_keys(['EnvelopeClass', 'access_type']) 1
0.000008s: [i=5]: before_try_iterate: DemoInterp
0.000012s: [i=5]: before_contribute_to_completion: DemoInterp
0.000012s: [i=5]: after_contribute_to_completion: DemoInterp
0.000061s: after_interpret_command
0.000003s: before_sending_response
2.734048s: total
```

2nd Tab:

```
0.000000s: before_request_payload_load
0.000230s: after_input_context_creation
0.000164s: [i=1]: before_consume_args: FirstArgInterp
0.000013s: [i=1]: before_try_iterate: FirstArgInterp
0.000005s: [i=1]: before_contribute_to_completion: FirstArgInterp
0.000003s: [i=1]: after_contribute_to_completion: FirstArgInterp
0.000176s: begin_query_envelopes: ClassFunction
0.000007s: before_cache_lookup
0.000047s: after_cache_lookup
0.000009s: end_query_envelopes: dict_keys(['EnvelopeClass']) 5
0.000004s: [i=2]: before_consume_args: DemoInterp
0.000008s: begin_query_envelopes: ClassFunction
0.000005s: before_cache_lookup
0.000023s: after_cache_lookup
0.000006s: end_query_envelopes: dict_keys(['EnvelopeClass', 'ActionType']) 2
0.000005s: begin_query_envelopes: ClassFunction
0.000004s: before_cache_lookup
0.000019s: after_cache_lookup
0.000006s: end_query_envelopes: dict_keys(['EnvelopeClass', 'ActionType', 'ObjectSelector']) 1
0.000006s: [i=2]: before_try_iterate: DemoInterp
0.000302s: begin_query_envelopes: ClassCluster
0.000003s: before_cache_lookup
0.000021s: after_cache_lookup
0.000006s: end_query_envelopes: dict_keys(['EnvelopeClass']) 1000
0.000003s: [i=3]: before_consume_args: DemoInterp
0.000005s: begin_query_envelopes: ClassCluster
0.000003s: before_cache_lookup
0.000015s: after_cache_lookup
0.000004s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity']) 100
0.000004s: begin_query_envelopes: ClassCluster
0.000003s: before_cache_lookup
0.000014s: after_cache_lookup
0.000004s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity', 'flow_stage']) 10
0.000003s: begin_query_envelopes: ClassCluster
0.000003s: before_cache_lookup
0.000013s: after_cache_lookup
0.000004s: end_query_envelopes: dict_keys(['EnvelopeClass', 'code_maturity', 'flow_stage', 'geo_region']) 1
0.000004s: [i=3]: before_try_iterate: DemoInterp
0.000010s: begin_query_envelopes: ClassHost
0.000003s: before_cache_lookup
0.000012s: after_cache_lookup
0.000003s: end_query_envelopes: dict_keys(['EnvelopeClass', 'cluster_name']) 10
0.000002s: [i=4]: before_consume_args: DemoInterp
0.000004s: begin_query_envelopes: ClassHost
0.000003s: before_cache_lookup
0.000013s: after_cache_lookup
0.000003s: end_query_envelopes: dict_keys(['EnvelopeClass', 'cluster_name', 'host_name']) 1
0.000003s: [i=4]: before_try_iterate: DemoInterp
0.000008s: begin_query_envelopes: access_type
0.000002s: before_cache_lookup
0.000012s: after_cache_lookup
0.000003s: end_query_envelopes: dict_keys(['EnvelopeClass']) 2
0.000002s: [i=5]: before_consume_args: DemoInterp
0.000004s: begin_query_envelopes: access_type
0.000003s: before_cache_lookup
0.000012s: after_cache_lookup
0.000003s: end_query_envelopes: dict_keys(['EnvelopeClass', 'access_type']) 1
0.000002s: [i=5]: before_try_iterate: DemoInterp
0.000004s: [i=5]: before_contribute_to_completion: DemoInterp
0.000007s: [i=5]: after_contribute_to_completion: DemoInterp
0.000048s: after_interpret_command
0.000002s: before_sending_response
0.001324s: total
```
