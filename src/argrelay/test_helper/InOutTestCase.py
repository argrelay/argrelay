from typing import Union, Type
from unittest import TestCase

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.relay_client import __main__
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder, LocalClientEnvMockBuilder
from argrelay.test_helper.LocalClientCommandFactory import LocalClientCommandFactory


class InOutTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Force restart of server for `LocalClient` before tests:
        LocalClientCommandFactory.local_server = None

    @classmethod
    def tearDownClass(cls) -> None:
        # Force restart of server for `LocalClient` after tests:
        LocalClientCommandFactory.local_server = None

    # TODO: wrap input into Dataclass which in turn can be created via builder (to have ability pre-build defaults for a set of tests).

    # TODO: Make generic validator be able to verify payload (not only `interp_ctx` passed from local client) - JSONPath?

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
            self.assertIsNotNone(delegator_class, "Capturing invocation data requires delegator class")

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

            # TODO: Be able to choose to verify output payload instead of server-side internal data
            #       (only available in tests when `LocalClient` and `LocalServer` are used).
            interp_ctx: InterpContext = command_obj.interp_ctx
            call_ctx: CallContext = command_obj.call_ctx

            # TODO: (JSONPath?) Currently, this verifier ensures what things exists.
            #       Add a way to ensure what things do not exists.
            #       For example,
            #       * no `data_envelope` number N.
            #       * `data_envelope` does not have field A.
            #       * `data_envelope` does not have value 'x' for field A.

            try:

                if expected_suggestions is not None:
                    # If `expected_suggestions`, verify them:
                    actual_suggestions = command_obj.response_dict[arg_values_]
                    self.assertEqual(expected_suggestions, actual_suggestions)

                if container_ipos_to_expected_assignments is not None:
                    self.verify_envelope_containers(
                        interp_ctx.envelope_containers,
                        container_ipos_to_expected_assignments,
                    )

                if delegator_class is not None:
                    self.assertEqual(
                        EnvMockBuilder.invocation_input.delegator_plugin_entry.plugin_module_name,
                        delegator_class.__module__,
                    )
                    self.assertEqual(
                        EnvMockBuilder.invocation_input.delegator_plugin_entry.plugin_class_name,
                        delegator_class.__name__,
                    )

                if envelope_ipos_to_field_values is not None:
                    self.verify_data_envelopes(
                        EnvMockBuilder.invocation_input.data_envelopes,
                        envelope_ipos_to_field_values,
                    )

            except:

                # Check if there are some obvious test input mistakes:

                if call_ctx.server_action == ServerAction.ProposeArgValues:
                    self.assertIsNone(delegator_class)
                    self.assertIsNone(envelope_ipos_to_field_values)
                elif call_ctx.server_action == ServerAction.DescribeLineArgs:
                    self.assertIsNone(expected_suggestions)
                    self.assertIsNone(delegator_class)
                    self.assertIsNone(envelope_ipos_to_field_values)
                elif call_ctx.server_action == ServerAction.RelayLineArgs:
                    self.assertIsNone(expected_suggestions)
                else:
                    raise RuntimeError

                # Rethrow previous error:
                raise

    def verify_envelope_containers(
        self,
        envelope_containers,
        container_ipos_to_expected_assignments,
    ):
        for container_ipos, expected_assignments in container_ipos_to_expected_assignments.items():
            try:
                if expected_assignments is None:
                    self.assertFalse(0 <= container_ipos < len(envelope_containers))
                else:
                    self.assertTrue(0 <= container_ipos < len(envelope_containers))
                    for arg_type, arg_value in expected_assignments.items():
                        try:
                            if arg_value is None:
                                self.assertTrue(
                                    arg_type not in
                                    envelope_containers
                                    [container_ipos].assigned_types_to_values
                                )
                            else:
                                self.assertEqual(
                                    arg_value,
                                    envelope_containers
                                    [container_ipos].assigned_types_to_values
                                    [arg_type]
                                )
                        except:
                            eprint(
                                f"container_ipos:{container_ipos} arg_type:{arg_type} arg_value:{arg_value}",
                            )
                            raise
            except:
                print(f"envelope_containers:\n{envelope_containers}")
                raise

    def verify_data_envelopes(
        self,
        data_envelopes,
        envelope_ipos_to_field_values,
    ):
        for envelope_ipos, field_values in envelope_ipos_to_field_values.items():
            try:
                if field_values is None:
                    self.assertFalse(
                        (0 <= envelope_ipos < len(data_envelopes))
                        and
                        # TODO: Maybe, for clarity, avoid adding such None data envelope?
                        # Containers with non-found `data_envelope`-s still contribute an entry to this list:
                        (data_envelopes[envelope_ipos] is not None)
                    )
                else:
                    self.assertTrue(
                        (0 <= envelope_ipos < len(data_envelopes))
                    )
                    for field_name, field_value in field_values.items():
                        try:
                            if field_value is None:
                                self.assertTrue(
                                    field_name not in
                                    data_envelopes[envelope_ipos]
                                )
                            else:
                                self.assertEqual(
                                    field_value,
                                    data_envelopes[envelope_ipos][field_name]
                                )
                        except:
                            eprint(
                                f"envelope_ipos:{envelope_ipos} field_name:{field_name} field_value:{field_value}",
                            )
                            raise

            except:
                print(f"data_envelopes:\n{data_envelopes}")
                raise
