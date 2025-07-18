from __future__ import annotations

from typing import (
    Type,
    Union,
)

from argrelay_api_plugin_server_abstract.DelegatorAbstract import DelegatorAbstract
from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_
from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.client_command_local.ClientCommandLocal import (
    ClientCommandLocal,
)
from argrelay_app_client.relay_client import __main__
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_test_infra.test_infra import parse_line_and_cpos
from argrelay_test_infra.test_infra.ClientCommandFactoryLocal import (
    ClientCommandFactoryLocal,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EnvMockBuilder,
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.InOutTestClass import InOutTestClass


class LocalTestClass(InOutTestClass):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #1.

    Tests which rely on `ClientLocal` to inspect internal-to-server `InterpContext`.
    """

    @classmethod
    def setUpClass(cls):
        InOutTestClass.setUpClass()
        # Force restart of the server for `ClientLocal` before tests:
        ClientCommandFactoryLocal.local_server = None

    @classmethod
    def tearDownClass(cls):
        InOutTestClass.tearDownClass()
        # Force restart of the server for `ClientLocal` after tests:
        ClientCommandFactoryLocal.local_server = None

    def verify_output_with_new_server_via_local_client(
        self,
        test_data: str,
        test_line: str,
        comp_type: CompType,
        expected_suggestions: Union[list[str], None],
        container_ipos_to_expected_assignments: Union[
            dict[int, dict[str, AssignedValue]], None
        ],
        delegator_class: Union[Type[DelegatorAbstract], None],
        envelope_ipos_to_prop_values: Union[dict[int, dict[str, str]], None],
    ):
        self.verify_output_via_local_client(
            test_data,
            test_line,
            comp_type,
            expected_suggestions,
            container_ipos_to_expected_assignments,
            None,
            delegator_class,
            envelope_ipos_to_prop_values,
            None,
            LocalClientEnvMockBuilder(),
        )

    def verify_output_via_local_client(
        self,
        test_data: str,
        test_line: str,
        comp_type: CompType,
        expected_suggestions: Union[list[str], None],
        container_ipos_to_expected_assignments: Union[
            dict[int, dict[str, AssignedValue]], None
        ],
        container_ipos_to_options_hidden_by_default_value: Union[
            dict[int, dict[str, list[str]]], None
        ],
        delegator_class: Union[Type[DelegatorAbstract], None],
        envelope_ipos_to_prop_values: Union[dict[int, dict[str, str]], None],
        expected_container_ipos_to_used_token_bucket: Union[
            dict[int, Union[int, None]], None
        ],
        init_env_mock_builder: EnvMockBuilder,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        if envelope_ipos_to_prop_values is not None:
            self.assertIsNotNone(delegator_class)

        if delegator_class is not None:
            init_env_mock_builder.set_capture_delegator_invocation_input(
                delegator_class
            )

        env_mock_builder = (
            init_env_mock_builder.set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_test_data_ids_to_load(
                [
                    test_data,
                ]
            )
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, ClientCommandLocal)

            # This server-side internal data `InterpContext` is only available in tests
            # when `ClientLocal` and `LocalServer` are used.
            interp_ctx: InterpContext = command_obj.interp_ctx
            call_ctx: CallContext = command_obj.call_ctx

            # TODO: TODO_32_99_70_35: (JSONPath?) Currently, this verifier ensures what things exists.
            #       Add a way to ensure what things do not exist.
            #       For example,
            #       * no `data_envelope` number N.
            #       * `data_envelope` does not have field A.
            #       * `data_envelope` does not have value 'x' for field A.

            actual_suggestions = None
            if expected_suggestions is not None:
                actual_suggestions = command_obj.response_dict[arg_values_]

            self.verify_response_data(
                call_ctx,
                actual_suggestions,
                container_ipos_to_expected_assignments,
                container_ipos_to_options_hidden_by_default_value,
                delegator_class,
                envelope_ipos_to_prop_values,
                expected_suggestions,
                interp_ctx.envelope_containers,
                expected_container_ipos_to_used_token_bucket,
            )
