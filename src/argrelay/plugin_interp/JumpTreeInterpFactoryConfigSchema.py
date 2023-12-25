from copy import deepcopy

from marshmallow import RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import (
    FuncTreeInterpFactoryConfigSchema,
    func_tree_interp_config_desc,
)

jump_tree_ = "jump_tree"


class JumpTreeInterpFactoryConfigSchema(FuncTreeInterpFactoryConfigSchema):
    class Meta:
        unknown = RAISE
        strict = True

    # This is a tree (`dict`) of arbitrary depth with `list[str]` leaves.
    # Ideally, this should be defined as nested `dict`,
    # but it is unknown how to do it in marshmallow.
    # Implements FS_91_88_07_23 jump tree.
    jump_tree = fields.Raw(
        required = True,
    )


_re_tree_interp_config_example = deepcopy(func_tree_interp_config_desc.dict_example)
_re_tree_interp_config_example.update({
    jump_tree_: [
        "relay_demo",
    ],
})

jump_tree_interp_config_desc = TypeDesc(
    dict_schema = JumpTreeInterpFactoryConfigSchema(),
    ref_name = JumpTreeInterpFactoryConfigSchema.__name__,
    dict_example = _re_tree_interp_config_example,
    default_file_path = "",
)
