import itertools
import time

from argrelay.client_spec.ShellContext import ShellContext, UNKNOWN_COMP_KEY
from argrelay.custom_integ.ServiceLoader import ServiceLoader
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.test_infra import parse_line_and_cpos, line_no
from argrelay.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder, wrap_instance_method
from argrelay.test_infra.LocalClientCommandFactory import LocalClientCommandFactory
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_39_58_01_91 query cache for performance - see results captured in `DistinctValuesQuery` docstring.

    It loops for each `DistinctValuesQuery` with TD_38_03_48_51 large generated test data.

    It runs single sample query (which actually results in multiple queries internally).

    Test can be done for both:
    *   use_mongomock_only = True: `mongomock`
    *   use_mongomock_only = False: `pymongo`
    """

    def test_perf_query_cache(self):

        use_mongomock_only: bool = True

        # Report:
        # *   Rows (1st index) = DistinctValuesQuery
        # *   Cols (2nd index) = object_multiplier
        # *   Cell = query time in ms
        report_table: dict[DistinctValuesQuery, dict[int, float]] = {}

        object_multiplier_values = [
            3,
            4,
            5,
            # Uncomment to increase data set sizes (test duration):
            # 6,
            # 7,
            # 8,
            # 9,
        ]

        distinct_value_queries = list(DistinctValuesQuery)

        test_cases = [
            (
                line_no(),
                "some_command goto service cm0 gr0 fs0 hs0 sn00 |", CompType.PrefixHidden,
                [],
            ),
        ]

        # Extend test cases with generated data
        # (Cartesian product with all `DistinctValuesQuery` and enabled|disabled cache):
        extended_test_cases: list[tuple[int, str, CompType, list[str], int, DistinctValuesQuery]] = []
        for test_case in test_cases:
            for extended_params in itertools.product(
                object_multiplier_values,
                # Run for different implementations
                # (even though it may not matter as they are called via the same instance method = same wrap mock to test):
                distinct_value_queries,
            ):
                extended_test_cases.append(test_case + extended_params)

        for extended_test_case in extended_test_cases:
            with self.subTest(extended_test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    object_multiplier,
                    distinct_values_query,
                ) = extended_test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                ServiceLoader.object_multiplier = object_multiplier

                env_mock_builder = (
                    ServerOnlyEnvMockBuilder()
                    .set_enable_query_cache(False)
                    .set_use_mongomock_only(use_mongomock_only)
                    .set_distinct_values_query(distinct_values_query)
                    .set_test_data_ids_to_load(["TD_38_03_48_51"])  # large generated
                )
                with env_mock_builder.build():
                    # Force restart of the server for `LocalClient` before tests:
                    LocalClientCommandFactory.local_server = None
                    # Start `LocalServer` with data:
                    server_config = server_config_desc.from_default_file()
                    local_server = LocalServer(server_config)
                    local_server.start_local_server()
                    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)

                    with wrap_instance_method(
                        local_server.query_engine,
                        local_server.query_engine._query_prop_values,
                    ) as method_wrap_mock:
                        call_ctx = ShellContext(
                            command_line = command_line,
                            cursor_cpos = cursor_cpos,
                            comp_type = comp_type,
                            is_debug_enabled = False,
                            comp_key = UNKNOWN_COMP_KEY,
                        ).create_call_context()

                        start_ns: int = time.time_ns()
                        response_dict = propose_arg_values_handler.handle_request(call_ctx)
                        stop_ns: int = time.time_ns()

                        diff_ns: int = stop_ns - start_ns

                        report_row = report_table.setdefault(distinct_values_query, {})
                        cell_value = diff_ns / 1_000_000_000
                        print(f"{distinct_values_query}:{object_multiplier}:{cell_value}")
                        report_row[object_multiplier] = cell_value

                        actual_suggestions = response_dict[arg_values_]
                        self.assertEqual(expected_suggestions, actual_suggestions)
                        self.assertEqual(method_wrap_mock.called, True)

                        local_server.stop_local_server()

        self.print_report(
            object_multiplier_values,
            distinct_value_queries,
            report_table,
        )

    def print_report(
        self,
        object_multiplier_values,
        distinct_value_queries,
        report_table,
    ):
        number_cell_width = 10

        # Header row:
        print(f"{'object_multiplier':>32}", end = "")
        for object_multiplier in object_multiplier_values:
            print(f"{object_multiplier:>{number_cell_width}}", end = "")
        print()

        print(f"{'object_count':>32}", end = "")
        for object_multiplier in object_multiplier_values:
            # There are 5 loops, each with `object_multiplier` items:
            print(f"{object_multiplier ** 5:>{number_cell_width}}", end = "")
        print()

        # delimiter:
        print(f"{'-' * 32:>32}", end = "")

        print()
        for distinct_values_query in distinct_value_queries:
            # Header column:
            print(f"{distinct_values_query.name:>32}", end = "")
            for object_multiplier in object_multiplier_values:
                print(f"{report_table[distinct_values_query][object_multiplier]:>{number_cell_width}.3f}", end = "")
            print()
