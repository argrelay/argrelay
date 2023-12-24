from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc

func_selector_tree_ = "func_selector_tree"

ignored_func_ids_list_ = "ignored_func_ids_list"

delegator_plugin_ids_ = "delegator_plugin_ids"
"""
List of delegator plugin ids (classes derived from `AbstractDelegator`) which are used to provide
function `data_envelope`-s to plug those functions into `func_selector_tree`.
"""


class FuncTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # This is a tree (`dict`) of arbitrary depth with `str` leaves.
    # Ideally, this should be defined as nested `dict`,
    # but it is unknown how to do it in marshmallow.
    # Implements FS_26_43_73_72 func tree.
    func_selector_tree = fields.Raw(
        required = True,
    )

    # It is an error if func id is reported by delegator in `delegator_plugin_ids` but missing in `func_selector_tree`.
    # To avoid the error, list such func id in `ignored_func_ids_list`.
    ignored_func_ids_list = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )

    delegator_plugin_ids = fields.List(
        fields.String(),
        required = True,
    )


func_tree_interp_config_example = {
    func_selector_tree_: {
        "list": {
            "repo": "list_repo_func",
            "service": "list_service_func",
        },
        "goto": {
            "repo": "goto_repo_func",
            "service": "goto_service_func",
        },
    },
    ignored_func_ids_list_: [
        "some_ignored_func",
    ],
    delegator_plugin_ids_: [
        "DelegatorPlugin1",
        "DelegatorPlugin2",
    ],
}

func_tree_interp_config_desc = TypeDesc(
    dict_schema = FuncTreeInterpFactoryConfigSchema(),
    ref_name = FuncTreeInterpFactoryConfigSchema.__name__,
    dict_example = func_tree_interp_config_example,
    default_file_path = "",
)
