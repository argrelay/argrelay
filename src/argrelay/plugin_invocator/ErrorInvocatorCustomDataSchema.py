from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

error_message_ = "error_message"

error_code_ = "error_code"


class ErrorInvocatorCustomDataSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    error_message = fields.String(
        required = False,
    )

    error_code = fields.Integer(
        required = False,
    )


error_invocator_custom_data_example = {
    error_message_: "INFO: command executed successfully: this is a stub",
    error_code_: 0,
}
error_invocator_custom_data_desc = TypeDesc(
    dict_schema = ErrorInvocatorCustomDataSchema(),
    ref_name = ErrorInvocatorCustomDataSchema.__name__,
    dict_example = error_invocator_custom_data_example,
    default_file_path = "",
)
