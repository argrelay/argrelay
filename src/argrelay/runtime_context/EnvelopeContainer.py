from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue


@dataclass
class EnvelopeContainer:
    """
    Combination of relevant config, user input and `data_envelope` from the store.
    """

    # A specs how to query `data_envelope` for this `EnvelopeContainer`:
    search_control: SearchControl = field(default_factory = lambda: SearchControl())

    # If found in the last query, it contains `data_envelope` based on `search_control`:
    data_envelope: dict = field(default_factory = lambda: None)

    # `data_envelope`-s found in the last query:
    found_count: int = field(default = 0)

    # TODO: Maybe rename to `context_types_to_values`?
    # TODO: Part of (or actually is?) `args_context`: FS_62_25_92_06:
    assigned_types_to_values: dict[str, AssignedValue] = field(default_factory = lambda: {})
    """
    All assigned args (from interpreted tokens) mapped as type:value which belong to `data_envelope`.
    """

    # TODO: Part of (or not?) `args_context` (FS_62_25_92_06) to support FS_13_51_07_97:
    remaining_types_to_values: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    All arg values per type left for suggestion given the `assigned_types_to_values`.
    """

    def update_curr_remaining_types_to_values(self, query_res):
        # reset:
        self.remaining_types_to_values.clear()
        self.found_count = 0

        # TODO: What if search result is huge? Blame data set designer?
        # find all remaining arg vals per arg type:
        for self.data_envelope in iter(query_res):
            self.found_count += 1
            # `arg_type` must be known:
            for arg_type in self.search_control.types_to_keys_dict.keys():
                # `arg_type` must be in one of the `data_envelope`-s found:
                if arg_type in self.data_envelope:
                    # `arg_type` must not be assigned/consumed:
                    if arg_type not in self.assigned_types_to_values.keys():
                        arg_val = self.data_envelope[arg_type]
                        if arg_type not in self.remaining_types_to_values:
                            val_list = []
                            self.remaining_types_to_values[arg_type] = val_list
                        else:
                            val_list = self.remaining_types_to_values[arg_type]
                        # Deduplicate: ensure unique `arg_value`-s:
                        if arg_val not in val_list:
                            val_list.append(arg_val)

    # See: FS_13_51_07_97:
    def populate_implicit_arg_values(self):
        """
        When `data_envelope` is singled out, all remaining `arg_type`-s become `ArgSource.ImplicitValue`.
        """
        # Filter as in: FS_31_70_49_15:
        for arg_type in self.search_control.keys_to_types_dict.values():
            if arg_type in self.data_envelope:
                if arg_type not in self.assigned_types_to_values:
                    assert arg_type in self.remaining_types_to_values
                    # Update only `assigned_types_to_values`,
                    # because `remaining_types_to_values` will be updated automatically.
                    self.assigned_types_to_values[arg_type] = AssignedValue(
                        self.data_envelope[arg_type],
                        ArgSource.ImplicitValue,
                    )

    @staticmethod
    def print_help(envelope_containers: list[EnvelopeContainer]):
        eprint()
        # TODO: print:
        #       * currently selected args in one line: key1:value2 key2:value2
        #       * not selected args types in multiple lines: type: value1 value2 ...
        # TODO: print values matching any of the arg types which have already been assigned
        # TODO: print conflicting values (two different implicit values)
        # TODO: print unrecognized tokens
        # TODO: for unrecognized token highlight by color all tokens with matching substring
        is_first_missing_found: bool = False
        for envelope_container in envelope_containers:
            eprint(envelope_container.search_control.envelope_class)

            for key_to_type_dict in envelope_container.search_control.keys_to_types_list:
                arg_key = next(iter(key_to_type_dict))
                arg_type = key_to_type_dict[arg_key]

                if arg_type in envelope_container.assigned_types_to_values:
                    eprint(TermColor.DARK_GREEN.value, end = "")
                    eprint(f"{arg_type}:", end = "")
                    eprint(
                        f" {envelope_container.assigned_types_to_values[arg_type].arg_value} " +
                        f"[{envelope_container.assigned_types_to_values[arg_type].arg_source.name}]",
                        end = ""
                    )
                    eprint(TermColor.RESET.value, end = "")
                elif arg_type in envelope_container.remaining_types_to_values:
                    eprint(TermColor.BRIGHT_YELLOW.value, end = "")
                    if not is_first_missing_found:
                        eprint(f"*{arg_type}:", end = "")
                        is_first_missing_found = True
                    else:
                        eprint(f"{arg_type}:", end = "")
                    eprint(f" ?", end = "")
                    eprint(TermColor.RESET.value, end = "")
                    eprint(
                        f" {'|'.join(envelope_container.remaining_types_to_values[arg_type])}",
                        end = ""
                    )
                else:
                    # The arg type is in the remaining but data have no arg values to suggest.
                    # Such arg types are shown because they are part of `search_control`.
                    # But they cannot be specified for current situation, otherwise, if already no data,
                    # any arg value assigned to such arg type would return no results.
                    eprint(TermColor.DARK_GRAY.value, end = "")
                    eprint(f"{arg_type}:", end = "")
                    eprint(" [none]", end = "")
                    eprint(TermColor.RESET.value, end = "")

                eprint()
