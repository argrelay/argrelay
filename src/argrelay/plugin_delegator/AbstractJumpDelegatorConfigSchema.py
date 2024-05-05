from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc

single_func_id_ = "single_func_id"
# TODO_10_72_28_05: This should be removed with FS_33_76_82_84 composite tree:
tree_abs_path_to_interp_id_ = "tree_abs_path_to_interp_id"

# TODO_40_10_18_32: add custom base to all schemas:
class AbstractJumpDelegatorConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    single_func_id = fields.String(
        required = True,
    )

    tree_abs_path_to_interp_id = fields.Dict(
        keys = fields.String(),
        # TODO_79_67_28_83: Express recursive dict schema:
        # This is a tree (`dict`) of arbitrary depth with `str` leaves.
        # Ideally, this should be defined as nested `dict`,
        # but it is unknown how to do it in marshmallow.
        values = fields.Raw(),
        required = True,
    )


abstract_jump_delegator_config_example = {
    single_func_id_: "intercept_invocation_func",
    tree_abs_path_to_interp_id_: {
        "relay_demo": {
            "intercept": "InterpTreeInterpFactory.default",
            "duplicates": {
                "intercept": "InterpTreeInterpFactory.default",
            },
        },
        "some_command": {
            "intercept": "InterpTreeInterpFactory.default",
            "duplicates": {
                "intercept": "InterpTreeInterpFactory.default",
            },
        },
    },
}

abstract_jump_delegator_config_desc = TypeDesc(
    dict_schema = AbstractJumpDelegatorConfigSchema(),
    ref_name = AbstractJumpDelegatorConfigSchema.__name__,
    dict_example = abstract_jump_delegator_config_example,
    default_file_path = "",
)
