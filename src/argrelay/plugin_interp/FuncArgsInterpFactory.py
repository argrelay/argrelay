from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.FuncArgsInterp import func_search_control_
from argrelay.plugin_interp.FuncArgsInterpFactoryConfigSchema import (
    func_args_interp_config_desc,
)
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import func_id_
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_


# TODO: At the moment `FuncTreeInterpFactory` derives from `FuncArgsInterpFactory`,
#       but it is conceptually confusing because `FuncTree` interp never interprets `FuncArgs`.
#       Introduce common base class?
class FuncArgsInterpFactory(AbstractInterpFactory):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        # FS_26_43_73_72 func tree: populated by `load_func_envelopes`
        # (as it needs tree context where this plugin instance is attached):
        self.func_paths: dict[str, list[list[str]]] = {}

    def validate_config(
        self,
    ):
        func_args_interp_config_desc.validate_dict(self.config_dict)

    def validate_loaded_data(
        self,
        static_data: "StaticData",
    ):
        self._validate_function_envelopes_unambiguously_qualified(static_data)

    def _validate_function_envelopes_unambiguously_qualified(
        self,
        static_data: "StaticData",
    ):
        """
        Verify that all props listed in `func_search_control` uniquely identify function

        Otherwise, functions which do not have unique "coordinates" with listed props will not be invokable.

        Plan:
        *   Find all func envelopes (those with `ReservedEnvelopeClass.ClassFunction`).
            TODO: Why function envelopes are not being filtered using `ReservedEnvelopeClass.ClassFunction`?
        *   Take those of them which have all prop names listed in `func_search_control_` plugin config.
            TODO: Why only those which have all prop names? Why sub-set is not needed?
        *   Make sure all prop values (ordered by prop names) have unique tuple.
        """

        # TODO: Fix this function: it is wrong by not using `interp_tree_path` and confusing by those TODO-s above.
        return

        for interp_tree_path, context_config in self.tree_path_config_dict:

            searchable_prop_names_list = SearchControl.convert_list_of_ordered_singular_dicts_to_unordered_dict(
                context_config[func_search_control_][keys_to_types_list_]
            ).values()

            all_prop_values_lists = []
            for data_envelope in static_data.data_envelopes:

                all_prop_names_exist = True
                searchable_prop_values_list = []
                for prop_name in searchable_prop_names_list:
                    if prop_name not in data_envelope:
                        all_prop_names_exist = False
                        break
                    else:
                        searchable_prop_values_list.append(data_envelope[prop_name])

                # TODO: clean up:
                print(
                    f"{self.plugin_instance_id} func_id: {data_envelope[instance_data_][func_id_]} searchable_prop_values_list: {searchable_prop_values_list}"
                )

                if all_prop_names_exist:
                    assert searchable_prop_values_list not in all_prop_values_lists
                    all_prop_values_lists.append(searchable_prop_values_list)
                else:
                    continue
