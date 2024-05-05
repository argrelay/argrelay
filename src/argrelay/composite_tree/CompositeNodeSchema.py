from copy import deepcopy

from marshmallow import fields, RAISE, post_load
from marshmallow_oneofschema import OneOfSchema

from argrelay.composite_tree.CompositeNode import (
    BaseNode,
    InterpTreeNode,
    ZeroArgNode,
    FuncTreeNode,
    TreePathNode,
)
from argrelay.composite_tree.CompositeNodeType import CompositeNodeType
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc

node_type_ = "node_type"
sub_tree_ = "sub_tree"

plugin_instance_id_ = "plugin_instance_id"
func_id_ = "func_id"
next_interp_ = "next_interp"
jump_path_ = "jump_path"


class BaseNodeSchema(ObjectSchema):
    """
    Schema for (base) FS_33_76_82_84 composite tree node.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = BaseNode

    node_type = None

    sub_tree = fields.Dict(
        keys = fields.String(),
        values = fields.Nested("CompositeNodeSchema"),
        required = False,
        allow_none = True,
        load_default = None,
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        """
        Implements inheritance as described here:
        https://stackoverflow.com/a/65668854/441652
        With modification:
        *   The class of the schema instance `self` is determined by `CompositeNodeSchema.type_field` (`node_type`).
        *   The schema instance `self` contains `model_class` to create via ctor with `node_type` to pass to ctor.
        *   The process is recursive to arbitrary depth of `BaseNode.sub_tree`.
        *   Note that `BaseNodeSchema` has no `node_type` (instead, it is defined in `CompositeNodeSchema`).
        """
        return type(self).model_class(
            **input_dict,
            node_type = self.node_type,
        )

class ZeroArgNodeSchema(BaseNodeSchema):
    """
    See FS_42_76_93_51 very first zero arg mapping interp.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = ZeroArgNode

    node_type = CompositeNodeType.zero_arg_node

    plugin_instance_id = fields.String(
        required = True,
    )


class InterpTreeNodeSchema(BaseNodeSchema):
    """
    See FS_01_89_09_24 interp tree.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = InterpTreeNode

    node_type = CompositeNodeType.interp_tree_node

    class NextInterpSchema(ObjectSchema):
        """
        Schema internal to `InterpTreeNodeSchema`.
        """

        class Meta:
            unknown = RAISE
            strict = True

        model_class = InterpTreeNode.NextInterp

        jump_path = fields.List(
            fields.String(),
            required = True,
        )

        plugin_instance_id = fields.String(
            required = True,
        )

    plugin_instance_id = fields.String(
        required = True,
    )

    next_interp = fields.Nested(
        NextInterpSchema(),
        required = True,
    )


class FuncTreeNodeSchema(BaseNodeSchema):
    """
    See FS_26_43_73_72 func tree.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = FuncTreeNode

    node_type = CompositeNodeType.func_tree_node

    func_id = fields.String(
        required = True,
    )


class TreePathNodeSchema(BaseNodeSchema):
    """
    See `CompositeNodeType.tree_path_node`.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = TreePathNode

    node_type = CompositeNodeType.tree_path_node


class CompositeNodeSchema(OneOfSchema):
    """
    Polymorphic schema for composite tree node - see:
    *   https://github.com/marshmallow-code/marshmallow-oneofschema
    *   https://stackoverflow.com/q/55092906/441652
    """

    type_field = node_type_

    def get_obj_type(
        self,
        obj,
    ):
        if isinstance(obj, ZeroArgNode):
            return ZeroArgNodeSchema.node_type.name
        elif isinstance(obj, InterpTreeNode):
            return InterpTreeNodeSchema.node_type.name
        elif isinstance(obj, FuncTreeNode):
            return FuncTreeNodeSchema.node_type.name
        elif isinstance(obj, TreePathNode):
            return TreePathNodeSchema.node_type.name
        else:
            raise Exception(f"Unknown object type: {obj.__class__.__name__}")

    type_schemas = {
        ZeroArgNodeSchema.node_type.name: ZeroArgNodeSchema,
        InterpTreeNodeSchema.node_type.name: InterpTreeNodeSchema,
        FuncTreeNodeSchema.node_type.name: FuncTreeNodeSchema,
        TreePathNodeSchema.node_type.name: TreePathNodeSchema,
    }


_base_node_example = {
    node_type_: CompositeNodeType.zero_arg_node.name,
    sub_tree_: None,
}

base_node_desc = TypeDesc(
    dict_schema = BaseNodeSchema(),
    ref_name = BaseNodeSchema.__name__,
    dict_example = _base_node_example,
    default_file_path = "",
)

_zero_arg_node_example = deepcopy(base_node_desc.dict_example)
_zero_arg_node_example.update({
    plugin_instance_id_: "some_plugin_instance_id",
})

zero_arg_node_desc = TypeDesc(
    dict_schema = ZeroArgNodeSchema(),
    ref_name = ZeroArgNodeSchema.__name__,
    dict_example = _zero_arg_node_example,
    default_file_path = "",
)

_interp_tree_node_example = deepcopy(base_node_desc.dict_example)
_interp_tree_node_example.update({
    plugin_instance_id_: "some_plugin_instance_id",
    next_interp_: {
        jump_path_: [
            "some_command",
        ],
        plugin_instance_id_: "some_plugin_instance_id",
    },
})

interp_tree_node_desc = TypeDesc(
    dict_schema = InterpTreeNodeSchema(),
    ref_name = InterpTreeNodeSchema.__name__,
    dict_example = _interp_tree_node_example,
    default_file_path = "",
)

_func_tree_node_example = deepcopy(base_node_desc.dict_example)
_func_tree_node_example.update({
    func_id_: "some_func_id",
})

func_tree_node_desc = TypeDesc(
    dict_schema = FuncTreeNodeSchema(),
    ref_name = FuncTreeNodeSchema.__name__,
    dict_example = _func_tree_node_example,
    default_file_path = "",
)

_tree_path_node_example = deepcopy(base_node_desc.dict_example)
_tree_path_node_example.update({})

tree_path_node_desc = TypeDesc(
    dict_schema = TreePathNodeSchema(),
    ref_name = TreePathNodeSchema.__name__,
    dict_example = _tree_path_node_example,
    default_file_path = "",
)
