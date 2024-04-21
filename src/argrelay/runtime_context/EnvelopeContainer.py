from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

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

    data_envelopes: list[dict] = field(default_factory = lambda: [])
    """
    These `data_envelope`-s are based on `search_control` for this `EnvelopeContainer` (and command line input).

    It contains only 0 or 1 `data_envelope` for performance reasons in case of:
    *   `ServerAction.ProposeArgValues` (Tab-completion)
    *   `ServerAction.DescribeLineArgs` (Alt+Shift+Q)
    See `QueryEngine.query_prop_values` and `QueryResult.data_envelopes`.

    It contains all N `data_envelope`-s in case of `ServerAction.RelayLineArgs`.
    See `QueryResult.data_envelopes`.
    """

    found_count: int = field(default = 0)
    """
    Counter of `data_envelope`-s found in the last query.
    """

    used_arg_bucket: Union[int, None] = field(default = None)
    """
    FS_97_64_39_94 `arg_bucket` (index) where args were consumed from for the current `envelope_container`.
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

    filled_types_to_values_hidden_by_defaults: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    FS_72_53_55_13: values hidden by defaults:
    This dict stores values which were hidden by applying defaults (see FS_72_40_53_00 fill control).
    Only keys for those `arg_type`-s which have `ArgSource.InitValue` in `assigned_types_to_values` are listed here.
    """

    def populate_implicit_arg_values(
        self,
    ) -> bool:
        """
        When possible arg_values are singled out, assign them as `ArgSource.ImplicitValue`.

        When `data_envelope` is singled out, all remaining single-value `arg_type`-s become `ArgSource.ImplicitValue`.

        Implements FS_13_51_07_97 singled out implicit values.

        Return:
        *   True if any value was assigned.
        *   False otherwise.
        """

        any_assigned = False
        # Filter as in: FS_31_70_49_15 search control:
        for arg_type in self.search_control.keys_to_types_dict.values():
            if arg_type not in self.assigned_types_to_values:
                if arg_type in self.remaining_types_to_values:
                    arg_values = self.remaining_types_to_values[arg_type]

                    # FS_06_99_43_60 list arg value:
                    # When a `data_envelope` is singled out, its array arg value will not be set as
                    # singled out via `ArgSource.ImplicitValue` (user can still select them explicitly).
                    # This is deliberate for now as the selection of specific value out of the array can be used
                    # by delegators to implement difference in behavior.

                    if len(arg_values) == 1:
                        del self.remaining_types_to_values[arg_type]
                        self.assigned_types_to_values[arg_type] = AssignedValue(
                            # single value:
                            arg_values[0],
                            ArgSource.ImplicitValue,
                        )
                        any_assigned = True
        return any_assigned
