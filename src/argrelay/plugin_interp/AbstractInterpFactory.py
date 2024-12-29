from __future__ import annotations

from copy import deepcopy

from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.PluginType import PluginType
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractInterpFactory(AbstractPluginServer):

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

        self.interp_tree_abs_paths: list[tuple[str, ...]] = []
        """
        All tree paths this plugin is plugged into.

        It is populated via `load_interp_tree_abs_paths`.
        """

        # Takes part in implementation of FS_01_89_09_24 interp tree:
        self.interp_tree_abs_paths_to_node_configs: dict[tuple[str, ...], dict] = {}
        """
        Classes derived from `AbstractInterp` (which are not direct plugins, not configured directly) are created by
        classed derived from `AbstractInterpFactory` (which are plugins with configs).
        Each `AbstractInterp` instance will require its own config called `interp_tree_node_config_dict` which are
        cloned/populated by `load_func_envelopes` and indexed by
        the abs path to the interp tree node in this `interp_tree_abs_paths_to_node_configs`.
        """

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.InterpFactoryPlugin

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        """
        This function is meant to be called prior to `load_func_envelopes` to
        let plugins know about all paths in the FS_01_89_09_24 `interp_tree` where they are plugged into.
        """
        pass

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> tuple[
        # mapped_func_ids:
        list[str],
        # index_props:
        list[str],
        # func_data_envelopes:
        list[dict],
    ]:
        """
        Load func `data_envelope`-s taking into account `interp_tree_abs_path`.

        Takes part in implementation of FS_01_89_09_24 interp tree.

        Returns:
        *   list of mapped `func_id`-s
        *   `index_prop`-s used by these `func_id`-s
        """
        if interp_tree_abs_path in self.interp_tree_abs_paths_to_node_configs:
            raise RuntimeError(f"`{interp_tree_abs_path}` has already been loaded")
        else:
            self.interp_tree_abs_paths_to_node_configs[interp_tree_abs_path] = deepcopy(self.plugin_config_dict)

        return (
            [],
            [],
            [],
        )

    def is_root_func_loader(
        self,
    ) -> bool:
        """
        Indicates that it implements:
        *   `get_func_dynamic_index_props`
        *   `get_func_data_envelopes`
        """
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor
        #       As of now, only `FirstArgInterpFactory` is supposed to return True.
        return False

    def get_func_dynamic_index_props(
        self,
    ) -> list[str]:
        """
        Provide `index_prop`-s of `index_model` for `funcs` if `is_root_func_loader` returns `True`.
        """
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor
        #       As of now, it is only supposed to be implemented by `FirstArgInterpFactory`.
        raise NotImplementedError

    def get_func_data_envelopes(
        self,
    ) -> list[dict]:
        """
        Provide loaded func `data_envelope`-s if `is_root_func_loader` returns `True`.
        """
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor
        #       As of now, it is only supposed to be implemented by `FirstArgInterpFactory`.
        raise NotImplementedError

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        raise NotImplementedError


class AbstractInterp:
    """
    `AbstractInterp` is NOT a plugin `AbstractInterpFactory` is.

    Interpreter processes command line sharing current state via :class:`InterpContext`.

    New instance of interpreter is created by (a plugin implementing) `AbstractInterpFactory` for each request.
    """

    instance_counter: int = 0
    """
    Instance counter per interp class.
    """

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
    ):
        self.interp_factory_id: str = interp_factory_id

        self.__class__.instance_counter += 1
        self.instance_number: int = self.instance_counter

        self.interp_tree_abs_path = list(interp_ctx.interp_tree_abs_path)

        self.interp_tree_node_config_dict: dict = interp_tree_node_config_dict
        """
        The configs for individual `AbstractInterp` are called `interp_tree_node_config_dict` and cloned/populated by
        `load_func_envelopes` based on their position in FS_01_89_09_24 interp tree.
        """

        self.interp_ctx: InterpContext = interp_ctx
        self.base_container_ipos: int = interp_ctx.curr_container_ipos

    def __str__(self) -> str:
        return f"fid: {self.interp_factory_id} path: {self.interp_ctx.interp_tree_abs_path} instance: {self.instance_number}"

    def consumes_args_at_once(self) -> bool:
        """
        Tell whether this interp consumes args one by one (FS_44_36_84_88) - see `consume_offered_args` for details.
        """
        return False

    def consume_dictated_args(self) -> bool:
        """
        Same as `consume_offered_args`, but for `dictated_arg`-s.
        """
        return False

    def consume_offered_args(self) -> bool:
        """
        Consume (usually) one arg at time: if consumed, return True, otherwise return False.

        If interp consumes all args at once,
        it has to override `consumes_args_at_once` to return `True`.

        Whether to consume more than one arg depends on whether it may
        violate FS_51_67_38_37 avoid impossible arg combinations.
        For example:
        *   FS_26_43_73_72 (func tree)
            All args (for func `data_container` or subsequent func `data_container` as arguments) has to be
            consumed one by one FS_44_36_84_88) because user is allowed to specify them in any order and
            consuming several at a time will violate FS_51_67_38_37 avoid impossible arg combinations.
        *   FS_01_89_09_24 (interp tree)
            All args can be consumed at once because user has to specify them in the order of the interp tree path.
        """
        return False

    def try_iterate(self) -> InterpStep:
        pass

    def has_fill_control(
        self,
    ) -> bool:
        """
        FS_72_53_55_13: See `DelegatorAbstract.has_fill_control` for more information.
        """
        return False

    def delegate_fill_control(
        self,
    ) -> bool:
        """
        FS_72_53_55_13: See `DelegatorAbstract.run_fill_control` for more information.
        """
        return False

    def propose_arg_completion(self) -> None:
        pass

    def next_interp(self) -> "AbstractInterp":
        """
        Return next interp factory id (or None).
        """
        return None
