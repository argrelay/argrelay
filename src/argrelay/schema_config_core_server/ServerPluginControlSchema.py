from __future__ import annotations

from marshmallow import RAISE, fields

from argrelay.composite_tree.CompositeNodeSchema import base_node_desc
from argrelay.composite_tree.CompositeForestSchema import composite_forest_desc
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerPluginControl import ServerPluginControl

first_interp_factory_id_ = "first_interp_factory_id"
composite_forest_ = "composite_forest"
reusable_config_data_ = "reusable_config_data"


class ServerPluginControlSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ServerPluginControl

    first_interp_factory_id = fields.String(
        required = True,
    )

    composite_forest = fields.Nested(
        composite_forest_desc.dict_schema,
        required = True,
    )

    # This `dict` provides a place to store arbitrary data.
    # YAML allows reusing any (substantially complex) data via aliases:
    # https://stackoverflow.com/a/48946813/441652
    # But `marshmallow` does not allow arbitrary data by default
    # (and it is kept that way to let garbage slip through).
    # This `dict` is ignored on load -
    # the data is used by YAML loader before it even reaches the schema validation.
    # See also values merge:
    # https://stackoverflow.com/a/46644785/441652
    reusable_config_data = fields.Dict(
        required = False,
        load_default = {},
    )


server_plugin_control_desc = TypeDesc(
    dict_schema = ServerPluginControlSchema(),
    ref_name = ServerPluginControlSchema.__name__,
    dict_example = {
        first_interp_factory_id_: "SomeInterp",
        composite_forest_: composite_forest_desc.dict_example,
    },
    default_file_path = "",
)
