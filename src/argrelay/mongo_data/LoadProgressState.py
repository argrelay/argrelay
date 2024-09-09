from dataclasses import dataclass, field


@dataclass
class LoadProgressState:
    """
    State and stats to track `data_envelope`-s loading progress.
    """
    envelope_per_col_i: int = field(default = 0)
    envelope_per_col_n: int = field(default = 0)
    total_envelope_i: int = field(default = 0)
    total_envelope_n: int = field(default = 0)
