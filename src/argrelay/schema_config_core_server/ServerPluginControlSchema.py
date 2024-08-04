from __future__ import annotations

from marshmallow import RAISE, fields

from argrelay.composite_forest.CompositeForestSchema import composite_forest_desc
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerPluginControl import ServerPluginControl

first_interp_factory_id_ = "first_interp_factory_id"
composite_forest_ = "composite_forest"


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


server_plugin_control_desc = TypeDesc(
    dict_schema = ServerPluginControlSchema(),
    ref_name = ServerPluginControlSchema.__name__,
    dict_example = {
        first_interp_factory_id_: "SomeInterp",
        composite_forest_: composite_forest_desc.dict_example,
    },
    default_file_path = "",
)
