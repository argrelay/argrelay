from dataclasses import dataclass


@dataclass
class QueryCacheConfig:
    enable_query_cache: bool = True

    query_cache_ttl_sec: int = 60

    query_cache_max_size_bytes: int = 1024 * 1024
