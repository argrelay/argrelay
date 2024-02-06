from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.TreeWalker import default_tree_leaf_

interp_selector_tree_ = "interp_selector_tree"


def validate_tree_node(interp_selector_sub_tree: dict):
    if isinstance(interp_selector_sub_tree, str):
        return
    elif isinstance(interp_selector_sub_tree, dict):
        for sub_tree_node in interp_selector_sub_tree.values():
            validate_tree_node(sub_tree_node)
    else:
        raise ValidationError(f"neither a str nor a dict: {interp_selector_sub_tree}")


class InterpTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    interp_selector_tree = fields.Dict(
        keys = fields.String(),
        # This is a tree (`dict`) of arbitrary depth with `str` leaves.
        # Ideally, this should be defined as nested `dict`,
        # but it is unknown how to do it in marshmallow.
        values = fields.Raw(),
        required = True,
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
        default_tree_leaf_: FuncTreeInterpFactory.__name__,
    },
}
tree_path_interp_factory_config_desc = TypeDesc(
    dict_schema = InterpTreeInterpFactoryConfigSchema(),
    ref_name = InterpTreeInterpFactoryConfigSchema.__name__,
    dict_example = tree_path_interp_factory_config_example,
    default_file_path = "",
)
