from marshmallow import fields, RAISE

from argrelay.composite_tree.CompositeForest import CompositeForest
from argrelay.composite_tree.CompositeNodeSchema import CompositeNodeSchema, node_type_, sub_tree_, zero_arg_node_desc
from argrelay.composite_tree.CompositeNodeType import CompositeNodeType
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc

tree_roots_ = "tree_roots"


class CompositeForestSchema(ObjectSchema):
    """
    Schema FS_33_76_82_84 composite trees combined into forest.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = CompositeForest

    tree_roots = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(CompositeNodeSchema()),
        required = True,
    )


_composite_forest_example = {
    tree_roots_: {
        "relay_demo": zero_arg_node_desc.dict_example,
    },
}

composite_forest_desc = TypeDesc(
    dict_schema = CompositeForestSchema(),
    ref_name = CompositeForestSchema.__name__,
    dict_example = _composite_forest_example,
    default_file_path = "",
)
