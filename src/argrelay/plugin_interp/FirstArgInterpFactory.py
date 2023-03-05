from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_interp_factory_config_desc
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterpFactory(AbstractInterpFactory):
    """
    Implements FS_42_76_93_51.
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
        first_arg_interp_factory_config_desc.validate_dict(config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> FirstArgInterp:
        return FirstArgInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )
