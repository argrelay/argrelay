from enum import Enum, auto


class CompositeInfoType(Enum):
    """
    Specifies info type extract-able from FS_33_76_82_84 the composite forest.
    """

    tree_abs_path_to_interp_id = auto()
    """
    Config for `tree_abs_path_to_interp_id` is used in delegator instances with `single_func_id` for special funcs.

    The `func_tree_node` is configured single `func_id` in the `sub_tree` (empty "" node name).

    The current path to `func_tree_node` is transformed back to the path of `zero_arg_node` leading to it.
    """

    # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor
    #       It is identical to `interp_tree`, but `interp_tree` does not include zero arg components.
    #       Consider making `interp_tree` global (with full paths including zero arg interp) -
    #       this way there will be no need for separate extraction of `zero_arg_interp_tree`.
    zero_arg_interp_tree = auto()
    """
    See FS_42_76_93_51 very first zero arg mapping interp.
    """

    jump_tree = auto()
    """
    See FS_91_88_07_23 jump tree.

    A tree of `CompositeNodeType.interp_tree_node` under `CompositeNodeType.zero_arg_node`
    with leaves set to absolute jump path within `composite_forest`.
    """

    interp_tree = auto()
    """
    See FS_01_89_09_24 interp tree.

    A tree of `CompositeNodeType.interp_tree_node` under `CompositeNodeType.zero_arg_node`
    with leaves set to `plugin-instance_id`-s derived from `AbstractInterpFactory`.
    """

    func_tree = auto()
    """
    See FS_26_43_73_72 func tree.

    A tree of `CompositeNodeType.func_tree_node` under `CompositeNodeType.interp_tree_node`
    with leaves set to `func_id`-s.
    """
