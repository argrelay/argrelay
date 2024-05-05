from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc

func_selector_tree_ = "func_selector_tree"

jump_tree_ = "jump_tree"


# TODO_40_10_18_32: add custom base to all schemas:
class FuncTreeInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # TODO_79_67_28_83: Express recursive dict schema:
    # This is a tree (`dict`) of arbitrary depth with `str` leaves.
    # Ideally, this should be defined as nested `dict`,
    # but it is unknown how to do it in marshmallow.
    # Implements FS_26_43_73_72 func tree.
    func_selector_tree = fields.Raw(
        required = True,
    )

    # TODO_79_67_28_83: Express recursive dict schema:
    # This is a tree (`dict`) of arbitrary depth with `list[str]` leaves.
    # Ideally, this should be defined as nested `dict`,
    # but it is unknown how to do it in marshmallow.
    # Implements FS_91_88_07_23 jump tree.
    jump_tree = fields.Raw(
        required = False,
    )


func_tree_interp_config_example = {
    func_selector_tree_: {
        "list": {
            "repo": "list_repo_func",
            "service": "list_service_func",
        },
        "diff": {
            "service": "diff_service_func",
        },
        "goto": {
            "repo": "goto_git_repo_func",
            "service": "goto_service_func",
        },
    },
    jump_tree_: [
        "relay_demo",
    ],
}

func_tree_interp_config_desc = TypeDesc(
    dict_schema = FuncTreeInterpFactoryConfigSchema(),
    ref_name = FuncTreeInterpFactoryConfigSchema.__name__,
    dict_example = func_tree_interp_config_example,
    default_file_path = "",
)
