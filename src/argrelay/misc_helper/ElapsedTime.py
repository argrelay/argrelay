from __future__ import annotations

import time
from dataclasses import dataclass
from typing import ClassVar

from argrelay.misc_helper import eprint


@dataclass
class ElapsedTime:
    """
    *   Instance holds a named timestamp.
    *   Class maintains a list of all instances (named timestamps) stored in order of measurements.

    At the moment, a static singleton is enough as perf measurements are done with single client.
    """

    name: str
    ts: int

    all_ts: ClassVar[list[ElapsedTime]] = []

    is_debug_enabled: bool = False
    """
    This is normally set based on `RequestContext.is_debug_enabled`.
    """

    def print(self, prev_ts: int):
        ElapsedTime.print_formatted(self.name, self.ts, self.ts - prev_ts)

    @classmethod
    def clear_measurements(cls):
        cls.all_ts.clear()

    @staticmethod
    def print_formatted(name: str, ts: int, diff: int):
        eprint(f"{diff / 1_000_000_000:f}s: {name}")

    @classmethod
    def measure(cls, name: str):
        cls.all_ts.append(ElapsedTime(name, time.time_ns()))

    @classmethod
    def print_all(cls):
        eprint()
        if cls.all_ts:
            first_ts = cls.all_ts[0]
            prev_ts = first_ts
            prev_ts.print(prev_ts.ts)
            remaining = cls.all_ts[1:]
        else:
            first_ts = None
            prev_ts = None
            remaining = []

        for ts in remaining:
            ts.print(prev_ts.ts)
            prev_ts = ts

        # total:
        if cls.all_ts:
            prev_ts.print_formatted("total", first_ts.ts, prev_ts.ts - first_ts.ts)

    @classmethod
    def print_all_if_debug(cls):
        if cls.is_debug_enabled:
            cls.print_all()
