"""
A helper module which is used only by a server (a client is not supposed to import it).

It can import any heavy modules as it is not import-latency-sensitive.

For common (client and server) helper, see `misc_helper_common`.
"""
import bisect


def insert_unique_to_sorted_list(
    sorted_list: list,
    list_value,
):
    il = bisect.bisect_left(sorted_list, list_value)
    if il <= len(sorted_list) and il == bisect.bisect_right(sorted_list, list_value):
        bisect.insort_left(sorted_list, list_value, il)
