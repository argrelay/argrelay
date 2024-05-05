from enum import Enum, auto


class CompositeInfoType(Enum):
    """
    Specifies info type extract-able from FS_33_76_82_84 the composite tree.
    """

    # TODO_10_72_28_05: This enum item should likely be factored out in the future.
    tree_abs_path_to_interp_id = auto()
    """
    Config for `tree_abs_path_to_interp_id` is used in delegator instances supporting single `func_id`.

    TODO_10_72_28_05: It seems very bespoke - think of getting rid of `tree_abs_path_to_interp_id`.
    *   Use current path to `func_tree_node`.
        NOTE: `tree_abs_path_to_interp_id` is used for special funcs
               with single `func_id` in the `sub_tree` (empty node name) of `func_tree_node`.
    *   Transform path to func back to path to dict entry.
    *   The value of dict entry is the `next_interp.plugin_instance_id` of the last `interp_tree_node`.
    """

    # TODO_10_72_28_05: This enum item should likely be factored out in the future.
    #                   Consider making `interp_tree` global (with full paths including zero arg interp) -
    #                   this way there will be no need for separate extraction of `zero_arg_interp_tree`.
    zero_arg_interp_tree = auto()
    """
    See FS_42_76_93_51 very first zero arg mapping interp.

    TODO: It is identical to `interp_tree`, but `interp_tree` does not include zero arg components.
    """


    jump_tree = auto()
    """
    See FS_91_88_07_23 jump tree.

    A tree of `CompositeNodeType.interp_tree_node` under `CompositeNodeType.zero_arg_node`
    with leaves set to absolute jump path within `composite_tree`.
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
