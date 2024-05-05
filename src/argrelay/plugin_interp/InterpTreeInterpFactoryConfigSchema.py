from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.composite_tree.DictTreeWalker import surrogate_node_id_

interp_selector_tree_ = "interp_selector_tree"

ignored_func_ids_list_ = "ignored_func_ids_list"


def validate_tree_node(interp_selector_sub_tree: dict):
    if isinstance(interp_selector_sub_tree, str):
        return
    elif isinstance(interp_selector_sub_tree, dict):
        for sub_tree_node in interp_selector_sub_tree.values():
            validate_tree_node(sub_tree_node)
    else:
        raise ValidationError(f"neither a str nor a dict: {interp_selector_sub_tree}")


# TODO_40_10_18_32: add custom base to all schemas:
class InterpTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    interp_selector_tree = fields.Dict(
        keys = fields.String(),
        # TODO_79_67_28_83: Express recursive dict schema:
        # This is a tree (`dict`) of arbitrary depth with `str` leaves.
        # Ideally, this should be defined as nested `dict`,
        # but it is unknown how to do it in marshmallow.
        values = fields.Raw(),
        required = True,
    )

    # TODO: FS_42_76_93_51: Decide already whether first zero arg interp deserves its future life.
    #                       This `ignored_func_ids_list` field is propagated down from
    #                       the first zero arg interp (needed for its logic as root plugin instance in the composite tree)
    #                       and it also needs to pass validation of this schema (which it converts its config to):
    # It is an error if `func_id` is published by enabled delegator but missing in `func_selector_tree`.
    # To avoid the error, list such func id in `ignored_func_ids_list`.
    ignored_func_ids_list = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )

    @validates_schema
    def validate_known(
        self,
        input_dict: dict,
        **kwargs,
    ):
        interp_selector_tree = input_dict[interp_selector_tree_]
        if not isinstance(interp_selector_tree, dict):
            raise ValidationError(f"not a dict: {interp_selector_tree}")
        validate_tree_node(interp_selector_tree)


tree_path_interp_factory_config_example = {
    interp_selector_tree_: {
        "some_command": "some_plugin_name",
        surrogate_node_id_: f"{FuncTreeInterpFactory.__name__}.default",
    },
    ignored_func_ids_list_: [
        "some_ignored_func",
    ],
}
tree_path_interp_factory_config_desc = TypeDesc(
    dict_schema = InterpTreeInterpFactoryConfigSchema(),
    ref_name = InterpTreeInterpFactoryConfigSchema.__name__,
    dict_example = tree_path_interp_factory_config_example,
    default_file_path = "",
)
