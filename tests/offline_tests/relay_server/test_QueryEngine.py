import itertools

from argrelay.client_spec.ShellContext import ShellContext, UNKNOWN_COMP_KEY
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_infra import parse_line_and_cpos, line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder, wrap_instance_method_on_instance
from argrelay.test_infra.ClientCommandFactoryLocal import ClientCommandFactoryLocal


class ThisTestClass(BaseTestClass):
    """
    Tests FS_39_58_01_91 query cache.
    """

    def test_enable_query_cache(self):
        """
        Test enabled and disabled cache has no diff and that cache actually works
        """

        test_cases = [
            (
                line_no(),
                "some_command host goto e| dev", CompType.PrefixHidden,
                [
                    "emea",
                ],
            ),
            (
                line_no(),
                "some_command service goto prod a|", CompType.PrefixHidden,
                [
                    "aaa",
                ],
            ),
        ]

        # Extend test cases with generated data
        # (Cartesian product with all `DistinctValuesQuery` and enabled|disabled cache):
        extended_test_cases: list[tuple[int, str, CompType, list[str], DistinctValuesQuery, bool]] = []
        for test_case in test_cases:
            for extended_params in itertools.product(
                # distinct_values_query:
                # Run for different implementations
                # (even though it may not matter as they are called via the same instance method = same wrap mock to test):
                DistinctValuesQuery,
                # enable_query_cache:
                [
                    True,
                    False,
                ],
            ):
                extended_test_cases.append(test_case + extended_params)

        for extended_test_case in extended_test_cases:
            with self.subTest(extended_test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    distinct_values_query,
                    enable_query_cache,
                ) = extended_test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                env_mock_builder = (
                    ServerOnlyEnvMockBuilder()
                    .set_enable_query_cache(enable_query_cache)
                    .set_distinct_values_query(distinct_values_query)
                    .set_test_data_ids_to_load(["TD_63_37_05_36"])  # demo
                )
                with env_mock_builder.build():
                    # Force restart of the server for `ClientLocal` before tests:
                    ClientCommandFactoryLocal.local_server = None
                    # Start `LocalServer` with data:
                    server_config = server_config_desc.obj_from_default_file()
                    plugin_config = plugin_config_desc.obj_from_default_file()
                    local_server = LocalServer(
                        server_config,
                        plugin_config,
                    )
                    local_server.start_local_server()
                    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)

                    # 1st run:
                    actual_suggestions_1st_run = "1st"
                    with wrap_instance_method_on_instance(
                        local_server.query_engine,
                        local_server.query_engine._query_prop_values,
                    ) as method_wrap_mock:
                        actual_suggestions_1st_run = self.run_completion(
                            ShellContext(
                                command_line = command_line,
                                cursor_cpos = cursor_cpos,
                                comp_type = comp_type,
                                is_debug_enabled = False,
                                comp_key = UNKNOWN_COMP_KEY,
                            ).create_call_context(),
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_wrap_mock,
                            # 1st time: processing is always called:
                            True,
                        )
                    # 2nd run:
                    actual_suggestions_2nd_run = "2nd"
                    with wrap_instance_method_on_instance(
                        local_server.query_engine,
                        local_server.query_engine._query_prop_values,
                    ) as method_wrap_mock:
                        actual_suggestions_2nd_run = self.run_completion(
                            ShellContext(
                                command_line = command_line,
                                cursor_cpos = cursor_cpos,
                                comp_type = comp_type,
                                is_debug_enabled = False,
                                comp_key = UNKNOWN_COMP_KEY,
                            ).create_call_context(),
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_wrap_mock,
                            # 2nd time: not called when cache is enabled, called when cache is disabled:
                            not enable_query_cache,
                        )
                    self.assertEqual(actual_suggestions_1st_run, actual_suggestions_2nd_run)

    def run_completion(
        self,
        call_ctx: CallContext,
        propose_arg_values_handler,
        expected_suggestions,
        method_wrap_mock,
        is_called,
    ):
        response_dict = propose_arg_values_handler.handle_request(call_ctx)
        actual_suggestions = response_dict[arg_values_]
        self.assertEqual(expected_suggestions, actual_suggestions)
        self.assertEqual(method_wrap_mock.called, is_called)
        return actual_suggestions
