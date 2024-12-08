from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc

single_func_id_ = "single_func_id"


# TODO: TODO_40_10_18_32: add custom base to all schemas:
class SchemaConfigDelegatorJumpAbstract(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    single_func_id = fields.String(
        required = True,
    )


abstract_jump_delegator_config_example = {
    single_func_id_: "func_id_intercept_invocation",
}

abstract_jump_delegator_config_desc = TypeDesc(
    dict_schema = SchemaConfigDelegatorJumpAbstract(),
    ref_name = SchemaConfigDelegatorJumpAbstract.__name__,
    dict_example = abstract_jump_delegator_config_example,
    default_file_path = "",
)
