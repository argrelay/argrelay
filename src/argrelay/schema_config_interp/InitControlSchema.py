from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_context.InitControl import InitControl

init_types_to_values_ = "init_types_to_values"
"""
Maps types to values for `init_control` (FS_46_96_59_05).
"""


class InitControlSchema(Schema):
    """
    Implements `init_control` (FS_46_96_59_05).
    """

    class Meta:
        unknown = RAISE
        strict = True

    init_types_to_values = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return InitControl(
            init_types_to_values = input_dict[init_types_to_values_],
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
