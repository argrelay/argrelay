from unittest import TestCase

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.relay_client import __main__
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):

    # noinspection PyMethodMayBeStatic
    def test_live_relay_line_args(self):
        test_line = "some_command goto service prod downstream wert-pd-1 |"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            EnvMockBuilder()
            .set_client_config_with_local_server(False)
            .set_mock_server_config_file_read(False)
            .set_mock_client_config_file_read(False)
            .set_run_mode(RunMode.InvocationMode)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.InvokeAction)
            .set_capture_invocator_invocation_input(ErrorInvocator)
        )
        with env_mock_builder.build():
            __main__.main()
            print(EnvMockBuilder.invocation_input)
            invocation_input = EnvMockBuilder.invocation_input
            self.assertEqual(
                ServiceEnvelopeClass.ClassService.name,
                invocation_input.data_envelopes[1][ReservedArgType.EnvelopeClass.name]
            )
            self.assertEqual(
                "prod-apac-downstream",
                invocation_input.data_envelopes[1][ServiceArgType.ClusterName.name]
            )
            self.assertEqual(
                "wert-pd-1",
                invocation_input.data_envelopes[1][ServiceArgType.HostName.name]
            )
            self.assertEqual(
                "tt1",
                invocation_input.data_envelopes[1][ServiceArgType.ServiceName.name]
            )
            self.assertTrue(True)

