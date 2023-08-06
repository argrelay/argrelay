from unittest import TestCase

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import LiveServerEnvMockBuilder


class ThisTestCase(TestCase):

    def test_live_describe_line_args(self):
        test_line = "some_command goto host pro| whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            LiveServerEnvMockBuilder()
            .set_run_mode(RunMode.CompletionMode)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.DescribeArgs)
        )
        with env_mock_builder.build():
            __main__.main()

        self.assertTrue(True)
