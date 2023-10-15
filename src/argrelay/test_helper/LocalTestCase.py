from __future__ import annotations

from typing import Union, Type

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.relay_client import __main__
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder, LocalClientEnvMockBuilder
from argrelay.test_helper.InOutTestCase import InOutTestCase
from argrelay.test_helper.LocalClientCommandFactory import LocalClientCommandFactory


class LocalTestCase(InOutTestCase):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #1.

    Tests which rely on `LocalClient` to inspect internal-to-server `InterpContext`.
    """

    @classmethod
    def setUpClass(cls):
        InOutTestCase.setUpClass()
        # Force restart of the server for `LocalClient` before tests:
        LocalClientCommandFactory.local_server = None

    @classmethod
    def tearDownClass(cls):
        InOutTestCase.tearDownClass()
        # Force restart of the server for `LocalClient` after tests:
        LocalClientCommandFactory.local_server = None

    def verify_output_with_new_server_via_local_client(
        self,
        test_data: str,
        test_line: str,
        comp_type: CompType,
        expected_suggestions: Union[list[str], None],
        container_ipos_to_expected_assignments: Union[dict[int, dict[str, str]], None],
        delegator_class: Union[Type[AbstractDelegator], None],
        envelope_ipos_to_field_values: Union[dict[int, dict[str, str]], None],
    ):
        self.verify_output_with_via_local_client(
            test_data,
            test_line,
            comp_type,
            expected_suggestions,
            container_ipos_to_expected_assignments,
            delegator_class,
            envelope_ipos_to_field_values,
            LocalClientEnvMockBuilder(),
        )

    def verify_output_with_via_local_client(
        self,
        test_data: str,
        test_line: str,
        comp_type: CompType,
        expected_suggestions: Union[list[str], None],
        container_ipos_to_expected_assignments: Union[dict[int, dict[str, str]], None],
        delegator_class: Union[Type[AbstractDelegator], None],
        envelope_ipos_to_field_values: Union[dict[int, dict[str, str]], None],
        init_env_mock_builder: EnvMockBuilder,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        if envelope_ipos_to_field_values is not None:
            self.assertIsNotNone(delegator_class)

        if delegator_class is not None:
            init_env_mock_builder.set_capture_delegator_invocation_input(delegator_class)

        env_mock_builder = (
            init_env_mock_builder
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_test_data_ids_to_load([
                test_data,
            ])
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)

            # This server-side internal data `InterpContext` is only available in tests
            # when `LocalClient` and `LocalServer` are used.
            interp_ctx: InterpContext = command_obj.interp_ctx
            call_ctx: CallContext = command_obj.call_ctx

            # TODO: (JSONPath?) Currently, this verifier ensures what things exists.
            #       Add a way to ensure what things do not exists.
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
                delegator_class,
                envelope_ipos_to_field_values,
                expected_suggestions,
                interp_ctx.envelope_containers,
            )
