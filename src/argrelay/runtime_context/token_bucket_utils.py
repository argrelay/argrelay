"""
Functions to work with FS_97_64_39_94 `token_bucket`-related data.
"""

from __future__ import annotations


def token_buckets_to_token_ipos_list(
    token_buckets: list[list[int]],
) -> list[int]:
    """
    Converts `token_bucket`-s to a flat token ipos list.
    """
    token_ipos_list = []
    for token_bucket in token_buckets:
        for token_ipos in token_bucket:
            token_ipos_list.append(token_ipos)
    return token_ipos_list
