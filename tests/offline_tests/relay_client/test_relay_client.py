from unittest import TestCase, skip

import responses

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.relay_client import __main__
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc, arg_values_
from argrelay.server_spec.const_int import BASE_URL_FORMAT
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import LiveServerEnvMockBuilder


class ThisTestCase(TestCase):
    """
    Client-only test via mocked `responses` lib (without spanning `argrelay` server).
    """

    @classmethod
    def setUpClass(cls):
        cls.base_URL = BASE_URL_FORMAT.format(**connection_config_desc.dict_example)

    # TODO: rewrite this test as `ProposeArgValuesRemoteClientCommand`
    #       does not use `requests` (to be test-able with `responses`)
    @skip
    @responses.activate
    def test_mocked_propose_arg_values(self):
        # given:

        test_line = "some_command pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        mocked_response = responses.Response(
            method = "POST",
            url = self.base_URL + ServerAction.ProposeArgValues.value,
            json = arg_values_desc.dict_example,
            status = 200,
            content_type = 'application/json'
        )
        responses.add(mocked_response)

        env_mock_builder = (
            LiveServerEnvMockBuilder()
            .set_client_config_dict(client_config_desc.dict_example)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_capture_stdout(True)
        )
        with env_mock_builder.build():
            # when:

            __main__.main()

            # then:

            self.assertTrue(
                "\n".join(arg_values_desc.dict_example[arg_values_])
                in
                env_mock_builder.actual_stdout.getvalue()
            )

    # TODO: add test for description
    # TODO: add test for invocation
