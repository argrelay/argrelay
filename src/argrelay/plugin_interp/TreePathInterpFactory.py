from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.TreePathInterp import TreePathInterp
from argrelay.plugin_interp.TreePathInterpFactoryConfigSchema import tree_path_interp_factory_config_desc
from argrelay.runtime_context.InterpContext import InterpContext


class TreePathInterpFactory(AbstractInterpFactory):
    """
    Implements FS_01_89_09_24.
    """

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        tree_path_interp_factory_config_desc.validate_dict(config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> TreePathInterp:
        return TreePathInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )
