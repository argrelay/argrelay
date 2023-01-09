from marshmallow import Schema, RAISE

from argrelay.misc_helper.TypeDesc import TypeDesc

"""
Schema for the result of interpretation taken from :class:`InterpContext`
"""


class InterpResultSchema(Schema):
    # TODO: This is supposed to be all details about parsing useful at least
    #       for equivalent of `InterpContext.print_help` (but on client-side)
    class Meta:
        unknown = RAISE
        ordered = True


interp_result_desc = TypeDesc(
    dict_schema = InterpResultSchema(),
    ref_name = InterpResultSchema.__name__,
    dict_example = {
    },
    default_file_path = "",
)
