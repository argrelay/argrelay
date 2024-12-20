from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from argrelay.enum_desc.ValueSource import ValueSource
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

    used_token_bucket: Union[int, None] = field(default = None)
    """
    FS_97_64_39_94 `token_bucket` (index) where args were consumed from for the current `envelope_container`.
    """

    # TODO: TODO_55_51_89_92: review and update `args_context`
    # TODO: Part of (or actually is?) `args_context`: FS_62_25_92_06:
    assigned_prop_name_to_prop_value: dict[str, AssignedValue] = field(default_factory = lambda: {})
    """
    All assigned args (from interpreted tokens) mapped as type:value which belong to `data_envelope`.
    """

    # TODO: TODO_55_51_89_92: review and update `args_context`
    # TODO: Part of (or not?) `args_context` (FS_62_25_92_06) to support FS_13_51_07_97 (single out implicit values):
    remaining_prop_name_to_prop_value: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    All `prop_value`-s per `prop_name` left as options to match `arg_value` given on the command line.

    When `arg_value` from command line matches one of the `prop_value`-s for one of the `prop_name`,
    this `prop_name` moves to `assigned_prop_name_to_prop_value`.
    """

    filled_prop_values_hidden_by_defaults: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    FS_72_53_55_13: values hidden by defaults:
    This dict stores values which were hidden by applying defaults (see FS_72_40_53_00 fill control).
    Only keys for those `prop_name`-s which have `ValueSource.default_value` in
    `assigned_prop_name_to_prop_value` are listed here.
    """

    def populate_implicit_arg_values(
        self,
    ) -> bool:
        """
        When possible `arg_value`-s are singled out, assign them as `ValueSource.implicit_value`.

        When `data_envelope` is singled out, all remaining single-value `prop_name`-s become `ValueSource.implicit_value`.

        Implements FS_13_51_07_97 singled out implicit values.

        Return:
        *   True if any value was assigned.
        *   False otherwise.
        """

        any_assigned = False
        # Filter as in: FS_31_70_49_15 search control:
        for prop_name in self.search_control.arg_name_to_prop_name_dict.values():
            if prop_name not in self.assigned_prop_name_to_prop_value:
                if prop_name in self.remaining_prop_name_to_prop_value:
                    prop_values = self.remaining_prop_name_to_prop_value[prop_name]

                    # FS_06_99_43_60 array `prop_value`:
                    # When a `data_envelope` is singled out, its array `prop_value` will not be set as
                    # singled out via `ValueSource.implicit_value` (user can still select them explicitly).
                    # This is deliberate for now as the selection of specific value out of the array can be used
                    # by delegators to implement difference in behavior.

                    if len(prop_values) == 1:
                        del self.remaining_prop_name_to_prop_value[prop_name]
                        self.assigned_prop_name_to_prop_value[prop_name] = AssignedValue(
                            # single value:
                            prop_values[0],
                            ValueSource.implicit_value,
                        )
                        any_assigned = True
        return any_assigned
