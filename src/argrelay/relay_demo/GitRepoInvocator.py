import subprocess

from argrelay.invocation_plugin.AbstractInvocator import AbstractInvocator
from argrelay.invocation_plugin.InvocationInput import InvocationInput
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.relay_demo.GitRepoArgType import GitRepoArgType
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataObjectSchema import object_data_, object_id_
from argrelay.schema_config_interp.FunctionObjectDataSchema import invocator_plugin_id_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc


class GitRepoInvocator(AbstractInvocator):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:
        # The first object (`DataObjectSchema`) is assumed to be of
        # `ReservedObjectClass.ClassFunction` with `FunctionObjectDataSchema` for its `object_data`:
        function_object = interp_ctx.assigned_types_to_values_per_object[0]
        invocator_plugin_id = function_object[object_data_][invocator_plugin_id_]
        invocation_input = InvocationInput(
            invocator_plugin_entry = server_config.plugin_dict[invocator_plugin_id],
            function_object = function_object,
            assigned_types_to_values_per_object = interp_ctx.assigned_types_to_values_per_object,
            interp_result = {},
            extra_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.function_object[object_id_] == "desc_repo":
            # The 2nd object (`DataObjectSchema`) is supposed to have `object_data` in its `object_data`:
            repo_object = invocation_input.assigned_types_to_values_per_object[1]
            abs_repo_path = repo_object[object_data_]["abs_repo_path"]
            # List Git repo dir:
            subproc = subprocess.run(
                [
                    "ls",
                    "-lrt",
                    abs_repo_path,
                ],
            )
            ret_code = subproc.returncode
            if ret_code != 0:
                raise RuntimeError

