from marshmallow import (
    fields,
    RAISE,
)

from argrelay_app_server.runtime_context.InitControl import InitControl
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc

init_types_to_values_ = "init_types_to_values"
"""
Maps types to values for `init_control` (FS_46_96_59_05).
"""


class InitControlSchema(ObjectSchema):
    """
    Implements `init_control` (FS_46_96_59_05).
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = InitControl

    init_types_to_values = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


init_control_desc = TypeDesc(
    dict_schema = InitControlSchema(),
    ref_name = InitControlSchema.__name__,
    dict_example = {
        init_types_to_values_: {
            "type_a": "TypeA",
            "type_b": "TypeB",
        },
    },
    default_file_path = "",
)
