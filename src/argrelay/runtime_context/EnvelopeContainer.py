from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue


@dataclass
class EnvelopeContainer:
    """
    Combination of relevant config, user input, and the last `data_envelope` found based on that.

    See also :class:`EnvelopeContainerSchema`.
    """

    search_control: SearchControl = field(default_factory = lambda: SearchControl())
    """
    A specs how to query `data_envelope` for this `EnvelopeContainer`.
    """

    data_envelope: dict = field(default = None)
    """
    If the last query finds (unique) single result,
    it contains `data_envelope` based on `search_control` and command line input.
    """

    found_count: int = field(default = 0)
    """
    Counter of `data_envelope`-s found in the last query.
    """

    # TODO: Maybe rename to `context_types_to_values`?
    # TODO: Part of (or actually is?) `args_context`: FS_62_25_92_06:
    assigned_types_to_values: dict[str, AssignedValue] = field(default_factory = lambda: {})
    """
    All assigned args (from interpreted tokens) mapped as type:value which belong to `data_envelope`.
    """

    # TODO: Part of (or not?) `args_context` (FS_62_25_92_06) to support FS_13_51_07_97 (single out implicit values):
    remaining_types_to_values: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    All arg values per arg type left as options to match arg value given on the command line.

    When arg value from command line matches one of the values, this arg type moves to `assigned_types_to_values`.
    """

    def populate_implicit_arg_values(self):
        """
        When `data_envelope` is singled out, all remaining `arg_type`-s become `ArgSource.ImplicitValue`.

        # Implements: FS_13_51_07_97
        """
        # Filter as in: FS_31_70_49_15:
        for arg_type in self.search_control.keys_to_types_dict.values():
            if arg_type not in self.assigned_types_to_values:
                if arg_type in self.remaining_types_to_values:
                    arg_values = self.remaining_types_to_values[arg_type]
                    if len(arg_values) == 1:
                        del self.remaining_types_to_values[arg_type]
                        self.assigned_types_to_values[arg_type] = AssignedValue(
                            arg_values[0],
                            ArgSource.ImplicitValue,
                        )
