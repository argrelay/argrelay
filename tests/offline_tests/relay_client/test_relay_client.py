from unittest import TestCase

import responses

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc, arg_values_
from argrelay.server_spec.const_int import PROPOSE_ARG_VALUES_PATH, BASE_URL_FORMAT
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_URL = BASE_URL_FORMAT.format(**connection_config_desc.dict_example)

    @responses.activate
    def test_mocked_propose_arg_values(self):
        # given:

        test_line = "some_command pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        mock_rdp_auth = responses.Response(
            method = "POST",
            url = self.base_URL + PROPOSE_ARG_VALUES_PATH,
            json = arg_values_desc.dict_example,
            status = 200,
            content_type = 'application/json'
        )
        responses.add(mock_rdp_auth)

        env_mock_builder = (
            EnvMockBuilder()
            .set_client_config_dict(client_config_desc.dict_example)
            .set_client_config_with_local_server(False)
            .set_mock_server_config_file_read(False)
            .set_run_mode(RunMode.CompletionMode)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_capture_stdout(True)
        )
        with env_mock_builder.build():
            __main__.main()

            self.assertTrue(
                "\n".join(arg_values_desc.dict_example[arg_values_])
                in
                env_mock_builder.actual_stdout.getvalue()
            )
