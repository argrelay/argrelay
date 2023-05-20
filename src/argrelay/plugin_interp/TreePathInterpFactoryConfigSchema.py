from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError

from argrelay.custom_integ.DemoInterpFactory import DemoInterpFactory
from argrelay.misc_helper.TypeDesc import TypeDesc

interp_selector_tree_ = "interp_selector_tree"

default_leaf_ = ""


def validate_tree_node(interp_selector_sub_tree: dict):
    if isinstance(interp_selector_sub_tree, str):
        return
    elif isinstance(interp_selector_sub_tree, dict):
        for sub_tree_node in interp_selector_sub_tree.values():
            validate_tree_node(sub_tree_node)
    else:
        raise ValidationError(f"neither a str nor a dict: {interp_selector_sub_tree}")


class TreePathInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    interp_selector_tree = fields.Dict(
        keys = fields.String(),
        # This is a tree (Dict) of arbitrary depth with leaves being of type String.
        # Ideally, this should be defined either String or nested Dict,
        # but it is unknown how to do it in marshmallow.
        values = fields.Raw(),
        required = True,
    )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        interp_selector_tree = input_dict[interp_selector_tree_]
        if not isinstance(interp_selector_tree, dict):
            raise ValidationError(f"not a dict: {interp_selector_tree}")
        validate_tree_node(interp_selector_tree)

tree_path_interp_factory_config_example = {
    interp_selector_tree_: {
        # TODO: This may not be currently configured plugin id:
        "intercept": f"{DemoInterpFactory.__name__}.intercept_func",
        default_leaf_: DemoInterpFactory.__name__,
    },
}
tree_path_interp_factory_config_desc = TypeDesc(
    dict_schema = TreePathInterpFactoryConfigSchema(),
    ref_name = TreePathInterpFactoryConfigSchema.__name__,
    dict_example = tree_path_interp_factory_config_example,
    default_file_path = "",
)
