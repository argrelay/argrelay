from marshmallow import (
    fields,
    RAISE,
    Schema,
)

from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc

error_message_ = "error_message"

error_code_ = "error_code"


class SchemaCustomDataDelegatorError(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    error_message = fields.String(
        required=False,
    )

    error_code = fields.Integer(
        required=False,
    )


error_delegator_stub_custom_data_example = {
    error_message_: "INFO: command executed successfully: demo implementation is a stub",
    error_code_: 0,
}
error_delegator_custom_data_desc = TypeDesc(
    dict_schema=SchemaCustomDataDelegatorError(),
    ref_name=SchemaCustomDataDelegatorError.__name__,
    dict_example=error_delegator_stub_custom_data_example,
    default_file_path="",
)
