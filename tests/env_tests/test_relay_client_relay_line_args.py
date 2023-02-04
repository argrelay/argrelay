from unittest import TestCase

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):

    # noinspection PyMethodMayBeStatic
    def test_live_relay_line_args(self):
        test_line = "relay_demo desc repo asdf/qwer/argrelay.git |"
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
        )
        with env_mock_builder.build():
            __main__.main()
