from marshmallow import Schema, RAISE, fields, ValidationError

from argrelay.misc_helper_common.TypeDesc import TypeDesc

ignored_func_ids_list_ = "ignored_func_ids_list"


def validate_tree_node(interp_selector_sub_tree: dict):
    if isinstance(interp_selector_sub_tree, str):
        return
    elif isinstance(interp_selector_sub_tree, dict):
        for sub_tree_node in interp_selector_sub_tree.values():
            validate_tree_node(sub_tree_node)
    else:
        raise ValidationError(f"neither a str nor a dict: {interp_selector_sub_tree}")


# TODO: TODO_40_10_18_32: add custom base to all schemas:
class InterpTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # TODO: FS_42_76_93_51: Decide already whether first zero arg interp deserves its future life.
    #       This `ignored_func_ids_list` field is propagated down from
    #       the first zero arg interp (needed for its logic as root plugin instance in the composite forest)
    #       and it also needs to pass validation of this schema (which it converts its config to):
    # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
    # It is an error if `func_id` is published by enabled delegator but missing in `func_selector_tree`.
    # To avoid the error, list such `func_id` in `ignored_func_ids_list`.
    ignored_func_ids_list = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )


tree_path_interp_factory_config_example = {
    ignored_func_ids_list_: [
        "func_id_some_ignored",
    ],
}
tree_path_interp_factory_config_desc = TypeDesc(
    dict_schema = InterpTreeInterpFactoryConfigSchema(),
    ref_name = InterpTreeInterpFactoryConfigSchema.__name__,
    dict_example = tree_path_interp_factory_config_example,
    default_file_path = "",
)
