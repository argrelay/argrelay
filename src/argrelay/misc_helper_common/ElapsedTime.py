from __future__ import annotations

import time

from argrelay.misc_helper_common import eprint


class ElapsedTime:
    """
    *   Instance holds a named timestamp.
    *   Class maintains a list of all instances (named timestamps) stored in order of measurements.

    At the moment, a static singleton is enough as perf measurements are done with single client.
    """

    all_ts: list[ElapsedTime] = []

    is_debug_enabled: bool = False
    """
    This is normally set based on `ShellContext.is_debug_enabled`.
    """

    def __init__(
        self,
        entry_name: str,
        entry_time: int,
    ):
        self.entry_name = entry_name
        self.entry_time = entry_time

    def print(self, prev_ts: int):
        ElapsedTime.print_formatted(
            self.entry_name,
            self.entry_time,
            self.entry_time - prev_ts,
        )

    @classmethod
    def clear_measurements(cls):
        cls.all_ts.clear()

    @staticmethod
    def print_formatted(name: str, ts: int, diff: int):
        eprint(f"{diff / 1_000_000_000:f}s: {name}")

    @classmethod
    def measure(cls, entry_name: str):
        cls.all_ts.append(ElapsedTime(entry_name, time.time_ns()))

    @classmethod
    def print_all(cls):
        eprint()
        if cls.all_ts:
            first_ts = cls.all_ts[0]
            prev_ts = first_ts
            prev_ts.print(prev_ts.entry_time)
            remaining = cls.all_ts[1:]
        else:
            first_ts = None
            prev_ts = None
            remaining = []

        for ts in remaining:
            ts.print(prev_ts.entry_time)
            prev_ts = ts

        # total:
        if cls.all_ts:
            prev_ts.print_formatted(
                "total",
                first_ts.entry_time,
                prev_ts.entry_time - first_ts.entry_time,
            )

    @classmethod
    def print_all_if_debug(cls):
        if cls.is_debug_enabled:
            cls.print_all()
