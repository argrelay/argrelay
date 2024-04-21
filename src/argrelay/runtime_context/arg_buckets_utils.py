"""
Functions to work with FS_97_64_39_94 `arg_bucket`-related data.
"""

from __future__ import annotations


def arg_buckets_to_token_ipos_list(
    arg_buckets: list[list[int]],
) -> list[int]:
    """
    Converts `arg_bucket`-s to a flat token ipos list.
    """
    token_ipos_list = []
    for arg_bucket in arg_buckets:
        for token_ipos in arg_bucket:
            token_ipos_list.append(token_ipos)
    return token_ipos_list
