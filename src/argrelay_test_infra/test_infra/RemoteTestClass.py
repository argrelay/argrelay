from __future__ import annotations

from typing import (
    Type,
    Union,
)

from argrelay_api_plugin_server_abstract.DelegatorAbstract import DelegatorAbstract
from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_
from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_app_client.client_command_remote.ClientCommandRemoteWorkerJson import (
    ClientCommandRemoteWorkerJson,
)
from argrelay_app_client.relay_client import __main__
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_test_infra.test_infra import parse_line_and_cpos
from argrelay_test_infra.test_infra.ClientServerTestClass import ClientServerTestClass
from argrelay_test_infra.test_infra.EnvMockBuilder import EnvMockBuilder


class RemoteTestClass(ClientServerTestClass):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #2.

    This class is similar to `LocalTestClass` as it is supposed to use `EnvMockBuilder`
    to capture server response, but, unlike `LocalTestClass`, requests go to separate OS process with running server.
    """

    # TODO: Allow intercepting subprocess.* invocation and asserting their input (e.g. whether specific command was invoked).
    def verify_output_via_remote_client(
        self,
        test_line: str,
        comp_type: CompType,
        expected_suggestions: Union[list[str], None],
        container_ipos_to_expected_assignments: Union[
            dict[int, dict[str, AssignedValue]], None
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

        # TODO: Make it possible to capture response for other `ServerAction`-s.
        #       At the moment, only `ServerAction.RelayLineArgs` is supported
        #       (because we are intercepting `invoke_action` on target `delegator_class`).
        #       But we could intercept on `*ClientResponseHandler.handle_response`:
        #       if non-optimized command is used for `ServerAction.ProposeArgValues`,
        #       it will always be JSON for all operations.
        assert comp_type is CompType.InvokeAction
        assert delegator_class is not None

        if delegator_class is not None:
            init_env_mock_builder.set_capture_delegator_invocation_input(
                delegator_class
            )

        env_mock_builder = (
            init_env_mock_builder.set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
        )
        with env_mock_builder.build():
            __main__.main()

            command_obj = __main__.main()
            assert isinstance(command_obj, ClientCommandRemoteWorkerJson)

            call_ctx = command_obj.call_ctx

            # TODO: TODO_32_99_70_35: (JSONPath?) Currently, this verifier ensures what things exists.
            #       Add a way to ensure what things do not exist.
            #       For example,
            #       * no `data_envelope` number N.
            #       * `data_envelope` does not have field A.
            #       * `data_envelope` does not have value 'x' for field A.

            actual_suggestions = None
            if expected_suggestions is not None:
                # TODO: This if-branch is unused - see if it is useful or clean up:
                # TODO: Consider intercepting `*ClientResponseHandler.handle_response`.
                #       At the moment, only intercepts for `ServerAction.RelayLineArgs` are supported
                #       (via `invoke_action` on target `delegator_class`) which make this access to
                #       response for `ServerAction.ProposeArgValues` fail:
                actual_suggestions = command_obj.response_dict[arg_values_]

            envelope_containers = None
            if delegator_class:
                envelope_containers = (
                    EnvMockBuilder.invocation_input.envelope_containers
                )

            self.verify_response_data(
                call_ctx,
                actual_suggestions,
                container_ipos_to_expected_assignments,
                None,
                delegator_class,
                envelope_ipos_to_prop_values,
                expected_suggestions,
                envelope_containers,
                expected_container_ipos_to_used_token_bucket,
            )
