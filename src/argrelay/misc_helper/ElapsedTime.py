from __future__ import annotations

import time
from dataclasses import dataclass
from typing import ClassVar

from argrelay.misc_helper import eprint


@dataclass
class ElapsedTime:
    """
    *   Object holds a named timestamp.
    *   Class maintains a list of all named timestamps stored in order of measurements.
    """

    name: str
    ts: int

    all_ts: ClassVar[list[ElapsedTime]] = []

    def print(self, prev_ts: int):
        eprint(f"{self.name}: {self.ts}: {(self.ts - prev_ts) / 1_000_000_000:f}s")

    @classmethod
    def measure(cls, name: str):
        cls.all_ts.append(ElapsedTime(name, time.time_ns()))

    @classmethod
    def print_all(cls):
        eprint()
        if cls.all_ts:
            prev_ts = cls.all_ts[0]
            prev_ts.print(prev_ts.ts)
            remaining = cls.all_ts[1:]
        else:
            prev_ts = None
            remaining = []

        for ts in remaining:
            ts.print(prev_ts.ts)
            prev_ts = ts
