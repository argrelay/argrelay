from argrelay.enum_desc.CompType import CompType
from argrelay.relay_client import __main__
from argrelay.test_infra import parse_line_and_cpos
from argrelay.test_infra.EnvMockBuilder import LiveServerEnvMockBuilder
from env_tests.ManualServerTestClass import ManualServerTestClassClass


# TODO: Do we really need this test? Why not using `RemoteTestClass` or `End2EndTestClass`?
class ThisTestClass(ManualServerTestClassClass):

    def test_live_describe_line_args(self):
        test_line = "some_command goto host pro| whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            LiveServerEnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.DescribeArgs)
        )
        with env_mock_builder.build():
            __main__.main()

        self.assertTrue(True)
