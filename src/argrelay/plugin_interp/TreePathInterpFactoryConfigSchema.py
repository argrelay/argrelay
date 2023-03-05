from marshmallow import Schema, RAISE, fields

from argrelay.custom_integ.DemoInterpFactory import DemoInterpFactory
from argrelay.misc_helper.TypeDesc import TypeDesc

interp_selector_tree_ = "interp_selector_tree"

default_leaf_ = ""


class TreePathInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    interp_selector_tree = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


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
