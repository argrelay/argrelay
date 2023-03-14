from unittest import TestCase

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class InOutTestCase(TestCase):

    # TODO: wrap input into Dataclass which in turn can be created via builder (to have ability pre-build defaults for a set of tests).
    def verify_output(
        self,
        test_data,
        test_line,
        run_mode,
        comp_type,
        expected_suggestions,
        envelope_ipos_to_expected_assignments,
        delegator_class,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        if delegator_class:
            init_env_mock_builder = EnvMockBuilder().set_capture_delegator_invocation_input(delegator_class)
        else:
            init_env_mock_builder = EnvMockBuilder()

        env_mock_builder = (
            init_env_mock_builder
            .set_run_mode(run_mode)
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
            interp_ctx = command_obj.interp_ctx

            # TODO: Currently, this verifier ensures what things exists.
            #       Add a way to ensure what things do not exists.
            #       For example,
            #       * no `data_envelope` number N.
            #       * `data_envelope` does not have field A.
            #       * `data_envelope` does not have value 'x' for field A.

            if envelope_ipos_to_expected_assignments:
                for envelope_ipos in envelope_ipos_to_expected_assignments.keys():
                    # Verify `envelope_container` of `envelope_ipos` exists in the list:
                    self.assertTrue(0 <= envelope_ipos < len(interp_ctx.envelope_containers))

            if run_mode == RunMode.CompletionMode:
                actual_suggestions = command_obj.response_dict[arg_values_]
                self.assertEqual(expected_suggestions, actual_suggestions)
                self.assertFalse(
                    envelope_ipos_to_expected_assignments,
                    "no assignments expected in `RunMode.CompletionMode`",
                )
                self.assertFalse(
                    delegator_class,
                    "no invocation expected in `RunMode.CompletionMode`",
                )
            elif run_mode == RunMode.InvocationMode:
                self.assertFalse(
                    expected_suggestions,
                    "no suggestions expected in `RunMode.InvocationMode`",
                )
                for envelope_ipos, expected_assignments in envelope_ipos_to_expected_assignments.items():
                    for arg_type, arg_value in expected_assignments.items():
                        if arg_value is None:
                            self.assertTrue(
                                arg_type not in
                                interp_ctx.envelope_containers
                                [envelope_ipos].assigned_types_to_values
                            )
                        else:
                            self.assertEqual(
                                arg_value,
                                interp_ctx.envelope_containers
                                [envelope_ipos].assigned_types_to_values
                                [arg_type]
                            )
