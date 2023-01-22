from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import keys_to_types_list_, envelope_class_


@dataclass
class EnvelopeContainer:
    """
    Combination of relevant config, user input and `data_envelope` from the store.
    """

    # A specs how to query `data_envelope` for this `EnvelopeContainer`:
    envelope_class_query: dict = field(default_factory = lambda: {})

    # If found in the last query, it contains `data_envelope` based on `envelope_class_query`:
    data_envelope: dict = field(default_factory = lambda: {})

    # `data_envelope`-s found in the last query:
    found_count: int = field(default = 0)

    # `keys_to_types_list` is a reference to `envelope_class_query[keys_to_types_list_]`:
    # Direct list to preserve order:
    keys_to_types_list: list[dict[str, str]] = field(init = False, default_factory = lambda: [])

    # `keys_to_types_dict` is derived from `keys_to_types_list`:
    # Direct dict for quick lookup:
    keys_to_types_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    # `types_to_keys_dict` is derived from `keys_to_types_dict`:
    # Reverse lookup:
    types_to_keys_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    # TODO: Part of to `args_context`: FD-2023-01-17--1:
    assigned_types_to_values: dict[str, AssignedValue] = field(default_factory = lambda: {})
    """
    All assigned args (from interpreted tokens) mapped as type:value which belong to `data_envelope`.
    """

    # TODO: Part of to `args_context`: FD-2023-01-17--1:
    remaining_types_to_values: dict[str, list[str]] = field(default_factory = lambda: {})
    """
    All arg values per type left for suggestion given the `assigned_types_to_values`.
    """

    def __post_init__(self):
        self._init_derived_fields()

    def init_envelope_class_query(self, envelope_class_query: dict):
        self.envelope_class_query.clear()
        self.envelope_class_query.update(envelope_class_query)
        self._init_derived_fields()

    def _init_derived_fields(self):
        if keys_to_types_list_ in self.envelope_class_query:
            self.keys_to_types_list = self.envelope_class_query[keys_to_types_list_]
        else:
            self.keys_to_types_list = []

        self.keys_to_types_dict = self.convert_list_of_ordered_singular_dicts_to_unordered_dict(
            self.keys_to_types_list
        )

        # generate reverse:
        self.types_to_keys_dict = {
            v: k for k, v in
            self.keys_to_types_dict.items()
        }

    @staticmethod
    def convert_list_of_ordered_singular_dicts_to_unordered_dict(dict_list: list[dict]) -> dict:
        """
        Convert ordered list[dict] (with dict having single { key: value }) into unordered dict { keys: values }.
        """
        converted_dict = {}
        for key_to_value_dict in dict_list:
            curr_key = next(iter(key_to_value_dict))
            curr_value = key_to_value_dict[curr_key]
            converted_dict[curr_key] = curr_value

        return converted_dict

    def update_curr_remaining_types_to_values(self, query_res):
        # reset:
        self.remaining_types_to_values.clear()
        self.found_count = 0

        # TODO: What if search result is huge? Blame data set designer?
        # find all remaining arg vals per arg type:
        for self.data_envelope in iter(query_res):
            self.found_count += 1
            # `arg_type` must be known:
            for arg_type in self.types_to_keys_dict.keys():
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

    # See: FD-2023-01-17--3:
    def populate_implicit_arg_values(self):
        """
        When `data_envelope` is singled out, all remaining `arg_type`-s become `ArgSource.ImplicitValue`.
        """
        for arg_type in self.keys_to_types_dict.values():
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
        #       * not selected args spaces in multiple lines: space: value1 value2 ...
        # TODO: print values matching any of the arg types which have already been assigned
        # TODO: print conflicting values (two different implicit values)
        # TODO: print unrecognized tokens
        # TODO: for unrecognized token highlight by color all tokens with matching substring
        is_first_missing_found: bool = False
        for envelope_container in envelope_containers:
            eprint(envelope_container.envelope_class_query[envelope_class_])

            for key_to_type_dict in envelope_container.keys_to_types_list:
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
                    eprint(TermColor.BRIGHT_RED.value, end = "")
                    if not is_first_missing_found:
                        eprint(f"*{arg_type}:", end = "")
                        is_first_missing_found = True
                    else:
                        eprint(f"{arg_type}:", end = "")
                    eprint(f" ?", end = "")
                    eprint(TermColor.RESET.value, end = "")

                eprint()
