from dataclasses import dataclass, field


@dataclass
class ProgressTracker:
    """
    State and stats to track `data_envelope`-s loading progress.
    """
    envelope_per_col_i: int = field(default = 0)
    envelope_per_col_n: int = field(default = 0)
    total_envelope_i: int = field(default = 0)
    total_envelope_n: int = field(default = 0)

    def assert_intermediate_progress(
        self,
    ):
        assert self.envelope_per_col_i <= self.envelope_per_col_n
        assert self.envelope_per_col_n <= self.total_envelope_n
        assert self.total_envelope_i <= self.total_envelope_n

    def assert_collection_final_progress(
        self,
    ):
        self.assert_intermediate_progress()
        assert self.envelope_per_col_i == self.envelope_per_col_n

    def assert_total_final_progress(
        self,
    ):
        self.assert_collection_final_progress()
        if self.total_envelope_i != self.total_envelope_n:
            raise AssertionError(
                f"`total_envelope_i` [{self.total_envelope_i}] == "
                f"`total_envelope_n` [{self.total_envelope_n}] "
                f"(not true)"
            )
