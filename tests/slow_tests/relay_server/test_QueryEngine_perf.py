from __future__ import annotations

import itertools
import time

from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_
from argrelay_app_client.client_spec.ShellContext import (
    ShellContext,
    UNKNOWN_COMP_KEY,
)
from argrelay_app_server.handler_request.ProposeArgValuesServerRequestHandler import (
    ProposeArgValuesServerRequestHandler,
)
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay_lib_server_plugin_demo.demo_service.ServiceLoader import ServiceLoader
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import (
    server_config_desc,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import plugin_config_desc
from argrelay_test_infra.test_infra import (
    ClientCommandFactoryLocal,
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    ServerOnlyEnvMockBuilder,
    wrap_instance_method_on_instance,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_39_58_01_91 query cache for performance - see results captured in `DistinctValuesQuery` docstring.

    It loops for each `DistinctValuesQuery` with TD_38_03_48_51 large generated test data.

    It runs single sample query (which actually results in multiple queries internally).

    Test can be done for both:
    *   use_mongomock = True: `mongomock`
    *   use_mongomock = False: `pymongo`
    """

    def test_perf_query_cache(self):

        # Switch between `mongomock` (True) and `pymongo` (False)
        use_mongomock_values: list[bool] = [
            True,
            # Uncomment to run with real MongoDB (requires setup):
            # False,
        ]

        # Report (multiple tables):
        # *   table selector A (1st index) = use_mongomock
        # *   Rows (2nd index) = DistinctValuesQuery
        # *   Cols (3rd index) = object_multiplier
        # *   Cell = query time in ms
        report_tables: dict[bool, dict[DistinctValuesQuery, dict[int, float]]] = {}

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
                "some_command goto service cm0 gr0 fs0 hs0 sn0|", CompType.PrefixHidden,
            ),
        ]

        # Extend test cases with generated data
        # (Cartesian product with all `DistinctValuesQuery`, use_mongomock_values, ...):
        extended_test_cases: list[tuple[
            int,
            str,
            CompType,
            int,
            bool,
            DistinctValuesQuery,
        ]] = []
        for test_case in test_cases:
            for extended_params in itertools.product(
                object_multiplier_values,
                use_mongomock_values,
                distinct_value_queries,
            ):
                extended_test_cases.append(test_case + extended_params)

        for extended_test_case in extended_test_cases:
            with self.subTest(extended_test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    object_multiplier,
                    use_mongomock,
                    distinct_values_query,
                ) = extended_test_case

                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                expected_suggestions = [
                    f"sn0{index_value}" for index_value in range(object_multiplier)
                    # Look up is set for `active` by default:
                    # Even (0, 2, ...) => active
                    # Odd (1, 3, ...) => passive
                    if index_value % 2 == 0
                ]

                ServiceLoader.object_multiplier = object_multiplier

                env_mock_builder = (
                    ServerOnlyEnvMockBuilder()
                    .set_enable_query_cache(False)
                    .set_use_mongomock(use_mongomock)
                    .set_distinct_values_query(distinct_values_query)
                    .set_test_data_ids_to_load(["TD_38_03_48_51"])  # large generated
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

                    with wrap_instance_method_on_instance(
                        local_server.query_engine,
                        local_server.query_engine._query_prop_values,
                    ) as method_wrap_mock:
                        call_ctx = ShellContext(
                            command_line = command_line,
                            cursor_cpos = cursor_cpos,
                            comp_type = comp_type,
                            is_debug_enabled = False,
                            comp_key = UNKNOWN_COMP_KEY,
                            input_data = None,
                        ).create_call_context()

                        print("---")
                        print(f"distinct_values_query: {distinct_values_query}")
                        print(f"use_mongomock: {use_mongomock}")
                        print(f"object_multiplier: {object_multiplier}")

                        start_ns: int = time.time_ns()
                        response_dict = propose_arg_values_handler.handle_request(call_ctx)
                        stop_ns: int = time.time_ns()

                        # Assert it actually works:
                        actual_suggestions = response_dict[arg_values_]
                        self.assertEqual(expected_suggestions, actual_suggestions)

                        diff_ns: int = stop_ns - start_ns

                        report_tables.setdefault(use_mongomock, {})
                        report_tables[use_mongomock].setdefault(distinct_values_query, {})

                        report_row = report_tables[use_mongomock][distinct_values_query]
                        cell_value = diff_ns / 1_000_000_000
                        report_row[object_multiplier] = cell_value

                        print(f"cell_value: {cell_value}")
                        print("---")

                        actual_suggestions = response_dict[arg_values_]
                        self.assertEqual(expected_suggestions, actual_suggestions)
                        self.assertEqual(method_wrap_mock.called, True)

                        local_server.stop_local_server()

        self.print_report(
            use_mongomock_values,
            object_multiplier_values,
            distinct_value_queries,
            report_tables,
        )

    # noinspection PyMethodMayBeStatic
    def print_report(
        self,
        use_mongomock_values: list[bool],
        object_multiplier_values: list[int],
        distinct_value_queries: list[DistinctValuesQuery],
        report_tables,
    ):
        number_cell_width = 10

        for use_mongomock in use_mongomock_values:

            # Delimiter:
            print("=" * 32)
            print(f"use_mongomock: {use_mongomock}")
            print()

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
                    print(
                        f"{report_tables[use_mongomock][distinct_values_query][object_multiplier]:>{number_cell_width}.3f}",
                        end = "",
                    )
                print()
