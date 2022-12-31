import contextlib
import io
import os
import sys
from unittest import TestCase, mock, skip
from unittest.mock import mock_open

import responses
import yaml

from argrelay.api_ext.ConnectionConfigSchema import connection_config_desc
from argrelay.api_ext.reley_client.ClientConfigSchema import client_config_desc
from argrelay.api_int.const_int import PROPOSE_ARG_VALUES_PATH, BASE_URL_FORMAT
from argrelay.api_int.data_schema.ArgValuesSchema import arg_values_desc
from argrelay.api_int.meta_data import CompType
from argrelay.relay_client import __main__
from test_argrelay import parse_line_and_cpos


class ThisTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_URL = BASE_URL_FORMAT.format(**connection_config_desc.dict_example)

    @skip  # test again running server
    def test_live_describe_line_args(self):
        test_line = "some_command pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        with mock.patch.dict(os.environ, {
            "COMP_LINE": command_line,
            "COMP_POINT": str(cursor_cpos),
            "COMP_TYPE": str(CompType.DescribeArgs.value),
            "COMP_KEY": "0",
        }):
            __main__.main()

        self.assertTrue(True)

    @skip  # test again running server
    def test_live_propose_arg_values(self):
        test_line = "some_command pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        with mock.patch.dict(os.environ, {
            "COMP_LINE": command_line,
            "COMP_POINT": str(cursor_cpos),
            "COMP_TYPE": str(CompType.PrefixShown.value),
            "COMP_KEY": "0",
        }):
            __main__.main()

        self.assertTrue(True)

    @skip  # test again running server
    def test_live_relay_line_args(self):
        test_argv = [
            "ignored/path/to/some.py",
            "some_command",
            "prod",
            "whatever",
        ]
        with mock.patch.object(sys, 'argv', test_argv):
            __main__.main()

        self.assertTrue(True)

    @responses.activate
    def test_mocked_propose_arg_values(self):
        # given:

        test_line = "some_comand pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        mock_rdp_auth = responses.Response(
            method = "POST",
            url = self.base_URL + PROPOSE_ARG_VALUES_PATH,
            json = arg_values_desc.dict_example,
            status = 200,
            content_type = 'application/json'
        )
        responses.add(mock_rdp_auth)

        client_config_yaml = yaml.dump(client_config_desc.dict_example)
        with mock.patch("builtins.open", mock_open(read_data = client_config_yaml)) as mock_file:
            self.assertTrue(open(client_config_desc.default_file_path).read() == client_config_yaml)
            stdout_f = io.StringIO()
            with contextlib.redirect_stdout(stdout_f):
                with mock.patch.dict(os.environ, {
                    "COMP_LINE": command_line,
                    "COMP_POINT": str(cursor_cpos),
                    "COMP_TYPE": str(CompType.PrefixShown.value),
                    "COMP_KEY": "0",
                }):
                    # when:

                    __main__.main()

        # then:

        mock_file.assert_called_with(client_config_desc.default_file_path)
        self.assertTrue("\n".join(arg_values_desc.dict_example["arg_values"]) in stdout_f.getvalue())
