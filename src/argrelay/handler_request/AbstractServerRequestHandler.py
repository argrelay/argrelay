import time

from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.UsageStatsEntry import UsageStatsEntry
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.server_spec.CallContext import CallContext


class AbstractServerRequestHandler:

    def __init__(
        self,
        local_server: LocalServer,
    ):
        self.local_server: LocalServer = local_server
        self.interp_ctx: InterpContext

    def handle_request(
        self,
        call_ctx: CallContext,
    ) -> dict:
        raise NotImplementedError

    def interpret_command(
        self,
        local_server: LocalServer,
        call_ctx: CallContext,
    ) -> None:
        parsed_ctx = ParsedContext.from_instance(call_ctx)
        # TODO: Split server_config and static_data in argrelay_server.yaml (both top level, not config including data):
        self.interp_ctx = InterpContext(
            parsed_ctx = parsed_ctx,
            interp_factories = local_server.server_config.interp_factories,
            action_delegators = local_server.server_config.action_delegators,
            query_engine = local_server.get_query_engine(),
            help_hint_cache = local_server.help_hint_cache,
        )
        self.interp_ctx.interpret_command(local_server.server_config.server_plugin_control.first_interp_factory_id)
        self.interp_ctx.print_debug()

    @staticmethod
    def _create_usage_stats_entry(
        call_ctx: CallContext,
    ) -> UsageStatsEntry:
        usage_stats_entry = UsageStatsEntry(
            server_action = call_ctx.server_action,
            comp_scope = call_ctx.comp_scope,
            server_ts_ns = time.time_ns(),
            client_version = call_ctx.client_version,
            client_conf_target = call_ctx.client_conf_target,
            client_user_id = call_ctx.client_uid,
            command_line = call_ctx.command_line,
            cursor_cpos = call_ctx.cursor_cpos,
        )
        return usage_stats_entry

    def _store_usage_stats_entry(
        self,
        call_ctx: CallContext,
    ) -> None:
        usage_stats_entry = self._create_usage_stats_entry(
            call_ctx = call_ctx,
        )
        self.local_server.usage_stats_store.store_usage_stats_entry(
            usage_stats_entry,
        )
