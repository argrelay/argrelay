import argrelay
from argrelay_app_client.client_command_local.ClientCommandLocal import (
    ClientCommandLocal,
)
from argrelay_app_client.client_spec.ShellContext import (
    get_client_conf_target,
    get_user_name,
    select_server_action,
)
from argrelay_app_client.relay_client import __main__
from argrelay_app_server.relay_server.UsageStatsEntry import UsageStatsEntry
from argrelay_app_server.relay_server.UsageStatsEntrySchema import (
    usage_stats_entry_desc,
)
from argrelay_lib_root.enum_desc.CompScope import CompScope
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_test_infra.test_infra import line_no_from_ctor
from argrelay_test_infra.test_infra.CustomTestCase import ShellInputTestCase
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EnvMockBuilder,
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Test FS_87_02_77_34 usage stats.
    """

    same_test_data_per_class = "TD_63_37_05_36"  # demo

    @classmethod
    def setUpClass(cls):
        LocalTestClass.setUpClass()
        # Clean usage stats:
        open(EnvMockBuilder.get_usage_stats_path(), "w").close()

    def test_FS_87_02_77_34_usage_stats(self):

        test_cases = [
            ThisTestCase(
                f"Cause {ServerAction.ProposeArgValues.name} stats",
                "some_command help |",
                CompType.PrefixShown,
                ServerAction.ProposeArgValues,
            ),
            ThisTestCase(
                f"Cause {ServerAction.DescribeLineArgs.name} stats",
                "some_command help interc|",
                CompType.DescribeArgs,
                ServerAction.DescribeLineArgs,
            ),
            ThisTestCase(
                f"Cause {ServerAction.RelayLineArgs.name} stats",
                "some_command help |",
                CompType.InvokeAction,
                ServerAction.RelayLineArgs,
            ),
        ]

        for test_case in test_cases:

            # Run two times:
            # *   mocked to observe calls to file writes
            # *   real to capture content
            for is_mocked_stats_file in [
                True,
                False,
            ]:
                test_case.is_mocked_stats_file = is_mocked_stats_file
                with self.subTest(test_case):

                    env_mock_builder = (
                        LocalClientEnvMockBuilder()
                        .set_command_line(test_case.command_line)
                        .set_cursor_cpos(test_case.cursor_cpos)
                        .set_comp_type(test_case.comp_type)
                        .set_mock_usage_stats_file_write(test_case.is_mocked_stats_file)
                        .set_test_data_ids_to_load(
                            [
                                self.__class__.same_test_data_per_class,
                            ]
                        )
                    )
                    with env_mock_builder.build():

                        self.assertEqual(
                            select_server_action(test_case.comp_type),
                            test_case.expected_server_action,
                        )

                        command_obj = __main__.main()
                        assert isinstance(command_obj, ClientCommandLocal)

                        if test_case.is_mocked_stats_file:
                            # Assert file writes:

                            file_mock = env_mock_builder.get_usage_stats_mock()

                            file_mock.assert_called_once_with(
                                env_mock_builder.get_usage_stats_path(), "a"
                            )
                            # Each JSON string per line is separated with new line:
                            file_mock().write.assert_called_with("\n")

                            # TODO: How to capture all the content written to the mocked file?
                            #       If that was possible, it could be asserted without
                            #       running tests twice to check real file

                        else:
                            # Assert file content:

                            # Get last JSON file line:
                            with open(
                                env_mock_builder.get_usage_stats_path()
                            ) as stats_usage_file:
                                for file_line in stats_usage_file:
                                    pass
                                last_line = file_line

                            usage_stats_entry: UsageStatsEntry = (
                                usage_stats_entry_desc.obj_from_yaml_str(last_line)
                            )

                            self.assertEqual(
                                usage_stats_entry,
                                UsageStatsEntry(
                                    server_action=test_case.expected_server_action,
                                    comp_scope=CompScope.from_comp_type(
                                        test_case.comp_type
                                    ),
                                    server_ts_ns=usage_stats_entry.server_ts_ns,
                                    client_conf_target=get_client_conf_target(),
                                    client_version=argrelay.__version__,
                                    client_user_id=get_user_name(),
                                    command_line=test_case.command_line,
                                    cursor_cpos=test_case.cursor_cpos,
                                ),
                            )


class ThisTestCase(ShellInputTestCase):

    def __init__(
        self,
        case_comment: str,
        test_line: str,
        comp_type: CompType,
        expected_server_action: ServerAction,
    ):
        super().__init__(
            line_no=line_no_from_ctor(),
            case_comment=case_comment,
        )
        self.set_test_line(test_line)
        self.set_comp_type(comp_type)
        self.expected_server_action = expected_server_action
        self.is_mocked_stats_file = True

    def __str__(
        self,
    ):
        return f"{super().__str__()}: {'mocked_file' if self.is_mocked_stats_file else 'real_file'}"
