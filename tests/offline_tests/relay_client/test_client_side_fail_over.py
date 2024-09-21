from __future__ import annotations

import os
import unittest
from dataclasses import asdict, replace
from typing import Union

import requests
import responses

from argrelay.client_command_remote.ClientCommandRemoteWorkerAbstract import get_server_index_file_path, random_file
from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.relay_client import __main__
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.server_spec.const_int import BASE_URL_FORMAT
from argrelay.test_infra import parse_line_and_cpos
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import LiveServerEnvMockBuilder

random_byte_value = b"\x07"

# TODO: TODO_30_69_19_14: client hangs with infinite spinner
#       Rewrite test to avoid using `requests`.
@unittest.skip
class ThisTestClass(BaseTestClass):
    """
    Test FS_93_18_57_91 client fail over to redundant servers.

    Client-only test (without spanning `argrelay` server).
    """

    @responses.activate
    def test_client_leaves_no_server_index_file_on_connection_failure(self):
        self.verify_client_fail_over_scenario(
            initial_file_content = None,
            # All failed:
            failed_server_indexes = list(range(len(self.get_test_server_connection_configs()))),
            residual_file_content = None,
        )

    @responses.activate
    def test_client_leaves_server_index_file_on_successful_connection(self):
        residual_file_content = str(
            int.from_bytes(random_byte_value, "little")
            %
            len(self.get_test_server_connection_configs())
        )
        self.verify_client_fail_over_scenario(
            initial_file_content = None,
            failed_server_indexes = [],
            residual_file_content = residual_file_content,
        )

    @responses.activate
    def test_client_fail_over_to_next_server(self):
        self.verify_client_fail_over_scenario(
            initial_file_content = "0",
            failed_server_indexes = [0],
            residual_file_content = "1",
        )

    @responses.activate
    def test_successful_connections_do_not_fail_over(self):
        self.verify_client_fail_over_scenario(
            initial_file_content = "1",
            failed_server_indexes = [0, 2],
            residual_file_content = "1",
        )

    @responses.activate
    def test_client_fail_over_with_negative_server_index_stored(self):
        self.verify_client_fail_over_scenario(
            initial_file_content = "-100",
            failed_server_indexes = [],
            # Stores immediately successful:
            # -100 % 3 = 2:
            residual_file_content = "2",
        )
        self.verify_client_fail_over_scenario(
            initial_file_content = "-100",
            # -100 % 3 = 2:
            failed_server_indexes = [2],
            # Stores next successful:
            residual_file_content = "0",
        )

    @responses.activate
    def test_start_index_beyond_available_connections_range(self):
        self.verify_client_fail_over_scenario(
            initial_file_content = "100",
            failed_server_indexes = [],
            # Stores immediately successful:
            # 100 % 3 = 1:
            residual_file_content = "1",
        )
        self.verify_client_fail_over_scenario(
            initial_file_content = "100",
            # 100 % 3 = 1:
            failed_server_indexes = [1],
            # Stores next successful:
            residual_file_content = "2"
        )

    # noinspection PyMethodMayBeStatic
    def get_test_server_connection_configs(
        self,
    ) -> list[ConnectionConfig]:
        """
        These connections just have to be different to differentiate them by mocked `responses`.
        """
        return [
            ConnectionConfig(
                server_host_name = "localhost",
                server_port_number = 10000,
            ),
            ConnectionConfig(
                server_host_name = "localhost",
                server_port_number = 10001,
            ),
            ConnectionConfig(
                server_host_name = "localhost",
                server_port_number = 10002,
            ),
        ]

    # noinspection PyMethodMayBeStatic
    def get_env_mock_builder(
        self,
        comp_type: CompType,
    ):
        # This test does not care about payload (it tests connection logic):
        test_line = "some_command pro|d whatever"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        client_config_obj: ClientConfig = client_config_desc.obj_from_default_file()
        client_config_obj = replace(
            client_config_obj,
            redundant_servers = self.get_test_server_connection_configs()
        )
        client_config_dict = client_config_desc.dict_from_input_obj(client_config_obj)

        env_mock_builder = (
            # Using "LiveServer*" because we do not manage server in the test,
            # but we mock communication with the server outside `EnvMockBuilder`:
            LiveServerEnvMockBuilder()
            .set_mock_client_config_file_read(True)
            .set_client_config_dict(client_config_dict)
            # TODO: TODO_72_51_13_18: test optimized requests:
            #       This will require abstracting mocking of connection success and connection failure.
            .set_client_config_to_optimize_completion_request(False)
            .set_show_pending_spinner(False)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_capture_stdout(True)
            .set_capture_stderr(True)
        )
        return env_mock_builder

    # noinspection PyMethodMayBeStatic
    def get_mocked_successful_response(
        self,
        connection_config: ConnectionConfig,
        server_action: ServerAction,
        response_body: dict,
    ):
        return responses.Response(
            method = responses.POST,
            url = BASE_URL_FORMAT.format(**asdict(connection_config)) + server_action.value,
            json = response_body,
            status = 200,
            content_type = "application/json",
        )

    # noinspection PyMethodMayBeStatic
    def get_mocked_failed_connection(
        self,
        connection_config: ConnectionConfig,
        server_action: ServerAction,
    ):
        return responses.Response(
            method = responses.POST,
            url = BASE_URL_FORMAT.format(**asdict(connection_config)) + server_action.value,
            body = requests.ConnectionError(),
            content_type = "application/json",
        )

    def verify_client_fail_over_scenario(
        self,
        initial_file_content: Union[None, str],
        failed_server_indexes: list[int],
        residual_file_content: Union[None, str],
    ):
        # given:

        comp_type: CompType = CompType.DescribeArgs
        response_dict = interp_result_desc.dict_example

        if initial_file_content is None:
            if os.path.exists(get_server_index_file_path()):
                os.remove(get_server_index_file_path())
        else:
            with open(get_server_index_file_path(), "w") as open_file:
                open_file.write(initial_file_content)

        for failed_server_index in failed_server_indexes:
            # It should not reference non-existing connections:
            self.assertTrue(failed_server_index < len(self.get_test_server_connection_configs()))
        # All values should be unique:
        self.assertEqual(
            len(set(failed_server_indexes)),
            len(failed_server_indexes),
        )

        for server_index, connection_config in enumerate(self.get_test_server_connection_configs()):
            if server_index in failed_server_indexes:
                responses.add(self.get_mocked_failed_connection(
                    connection_config,
                    ServerAction.DescribeLineArgs,
                ))
            else:
                responses.add(self.get_mocked_successful_response(
                    connection_config,
                    ServerAction.DescribeLineArgs,
                    response_dict,
                ))

        # It should be successful unless all connection configs fail:
        is_connection_successful: bool = (
            set(failed_server_indexes)
            !=
            set(range(len(self.get_test_server_connection_configs())))
        )

        # when:

        env_mock_builder = self.get_env_mock_builder(comp_type)
        if initial_file_content is None:
            # If there is no initial file content, bytes from random file are used:
            env_mock_builder.file_mock.add_path_data(
                random_file,
                random_byte_value,
            )
        with env_mock_builder.build():
            if is_connection_successful:
                __main__.main()
            else:
                with self.assertRaises(SystemExit) as cm:
                    __main__.main()
                self.assertEqual(
                    cm.exception.code,
                    ClientExitCode.ConnectionError.value,
                )

        # then:

        file_exists = os.path.exists(get_server_index_file_path())
        if is_connection_successful:
            self.assertTrue(file_exists)
        else:
            if initial_file_content is None:
                self.assertFalse(file_exists)
            else:
                self.assertTrue(file_exists)

        if residual_file_content is not None:
            with open(get_server_index_file_path(), "r") as open_file:
                self.assertEqual(
                    residual_file_content,
                    open_file.read(),
                )
