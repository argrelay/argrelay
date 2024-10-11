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

    # A specs how to query `data_envelope` for this `EnvelopeContainer` (which arg types to use).
    # Direct list to preserve order:
    keys_to_props_list: list[dict[str, str]] = field(default_factory = lambda: [])

    # `keys_to_props_dict` is derived from `keys_to_props_list`:
    # Direct dict for quick lookup:
    keys_to_props_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    # `props_to_keys_dict` is derived from `keys_to_props_dict`:
    # Reverse lookup:
    props_to_keys_dict: dict[str, str] = field(init = False, default_factory = lambda: {})

    def __post_init__(self):
        self._init_derived_fields()
        self._verify_prop_names_consistency()

    def _init_derived_fields(self):
        self.keys_to_props_dict = self.convert_list_of_ordered_singular_dicts_to_unordered_dict(
            self.keys_to_props_list
        )

        # generate reverse:
        self.props_to_keys_dict = {
            v: k for k, v in
            self.keys_to_props_dict.items()
        }

    def _verify_prop_names_consistency(self):
        """
        Make sure `prop_name`-s specified in `props_to_values_dict` for FS_46_96_59_05 `init_control`
        are also among `prop_name`-s specified for FS_31_70_49_15 `search control`.
        """
        for prop_name in self.props_to_values_dict:
            assert prop_name in self.props_to_keys_dict

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
