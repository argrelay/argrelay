from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerPluginControl import ServerPluginControl

first_interp_factory_id_ = "first_interp_factory_id"
reusable_config_data_ = "reusable_config_data"


class ServerPluginControlSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    first_interp_factory_id = fields.String(
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

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return ServerPluginControl(
            first_interp_factory_id = input_dict[first_interp_factory_id_],
            # `reusable_config_data` is ignored
        )


server_plugin_control_desc = TypeDesc(
    dict_schema = ServerPluginControlSchema(),
    ref_name = ServerPluginControlSchema.__name__,
    dict_example = {
        first_interp_factory_id_: "SomeInterp",
    },
    default_file_path = "",
)
