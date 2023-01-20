from argrelay.misc_helper.AbstractPlugin import AbstractPlugin
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractInvocator(AbstractPlugin):
    """
    Invocator plugin implements two sides:
    *   server-side `populate_invocation_input` prepares data in :class:`InvocationInput` (whatever is necessary)
    *   client-side `invoke_action` uses data in :class:`InvocationInput` to execute the action anyway it can

    To simplify reasoning, ensure that both server-side and client-side:
    *   have access to the same code (non-breaking differences are possible, but same code version ensures that)
    *   share data only via :class:`InvocationInput`
    """

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:
        """
        Server-side entry point.
        The plugin instance is used by server after `AbstractPlugin.activate_plugin`.
        """
        pass

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        """
        Client-side (static) entry point.
        The plugin instance is used by client:
        *   without instantiating
        *   without providing `AbstractPlugin.config_dict`
        *   without calling `AbstractPlugin.activate_plugin`
        """
        pass
