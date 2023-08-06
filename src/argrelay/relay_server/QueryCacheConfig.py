from dataclasses import dataclass, field


@dataclass
class QueryCacheConfig:
    enable_query_cache: bool = field(default = True)

    query_cache_ttl_sec: int = field(default = 60)

    query_cache_max_size_bytes: int = field(default = 1024 * 1024)
