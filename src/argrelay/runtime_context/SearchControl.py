from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchControl:
    """
    Implements:
    *   FS_46_96_59_05 `init_control`
    *   FS_31_70_49_15 `search control`

    See also `SearchControlSchema`.
    """

    collection_name: str = field(default_factory = lambda: None)
    """
    MongoDB collection to search `data_envelope`-s in.
    """

    props_to_values_dict: dict[str, str] = field(default_factory = lambda: {})

    # FS_10_93_78_10: `arg_name_to_prop_name_map`:
    # A spec to query `data_envelope`-s for this `EnvelopeContainer`:
    # *   which `prop_name`-s to use in query
    # *   which `arg_name` is mapped into which `prop_name`
    # a `list` to preserve order:
    arg_name_to_prop_name_map: list[dict[str, str]] = field(default_factory = lambda: [])

    # `arg_name_to_prop_name_dict` is derived from `arg_name_to_prop_name_map`:
    # a `dict` for quick lookup:
    arg_name_to_prop_name_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    # `prop_name_to_arg_name_dict` is derived from `arg_name_to_prop_name_map`:
    # a `dict` for reverse lookup:
    prop_name_to_arg_name_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    def __post_init__(self):
        self._init_derived_fields()
        self._verify_prop_names_consistency()

    def _init_derived_fields(self):
        # generate `dict`:
        self.arg_name_to_prop_name_dict = self.convert_list_of_ordered_singular_dicts_to_unordered_dict(
            self.arg_name_to_prop_name_map,
        )

        # generate reverse `dict`:
        self.prop_name_to_arg_name_dict = {
            v: k for k, v in
            self.arg_name_to_prop_name_dict.items()
        }

    def _verify_prop_names_consistency(self):
        """
        Make sure `prop_name`-s specified in `props_to_values_dict` for FS_46_96_59_05 `init_control`
        are also among `prop_name`-s specified for FS_31_70_49_15 `search control`.
        """
        for prop_name in self.props_to_values_dict:
            assert prop_name in self.prop_name_to_arg_name_dict

    @staticmethod
    def convert_list_of_ordered_singular_dicts_to_unordered_dict(
        arg_name_to_prop_name_map: list[dict],
    ) -> dict:
        """
        Convert ordered list[dict] (with dict having single { key: value }) into unordered dict { keys: values }.
        """
        converted_dict = {}
        for arg_name_to_prop_name_entry in arg_name_to_prop_name_map:
            arg_name = next(iter(arg_name_to_prop_name_entry))
            prop_name = arg_name_to_prop_name_entry[arg_name]
            converted_dict[arg_name] = prop_name

        return converted_dict
