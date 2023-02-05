"""
Mock environment (env vars, command line args, file access, database, etc.) for `argrelay` client or server
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
from contextlib import ExitStack
from dataclasses import dataclass, field
from unittest import mock

import mongomock
import pkg_resources
import yaml

import argrelay
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.mongo_data import MongoClientWrapper
from argrelay.relay_demo.GitRepoLoader import GitRepoLoader
from argrelay.relay_demo.GitRepoLoaderConfigSchema import is_plugin_enabled_
from argrelay.relay_demo.ServiceLoader import ServiceLoader
from argrelay.relay_demo.ServiceLoaderConfigSchema import test_data_ids_to_load_
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.schema_config_core_client.ClientConfigSchema import use_local_requests_, client_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_server_, use_mongomock_only_
from argrelay.schema_config_core_server.MongoServerConfigSchema import start_server_
from argrelay.schema_config_core_server.ServerConfigSchema import (
    mongo_config_,
    server_config_desc,
    plugin_dict_,
)
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_helper.OpenFileMock import OpenFileMock


@dataclass
class EnvMockBuilder:
    """
    All-in-one mock support which sets up the mocks and cleans them up as Python's Context Manager.

    For example:

    *   Mock env vars or `sys.argv` used by Bash to communicate input to argrelay client - see usage of:

        *   _mock_client_input_in_completion_mode
        *   _mock_client_input_in_invocation_mode_with_args
        *   _mock_client_input_in_invocation_mode_with_line

    *   Mock server and client config files - see usage of:

        *   set_server_config_dict
        *   set_client_config_dict

    *   Capture `stdout` and `stderr` - see usage of:

        *   set_capture_stdout
        *   set_capture_stderr

    *   Whether client uses `LocalClient`/`LocalServer` or `RemoteClient` with `CustomFlaskApp` - see usage of:

        *   set_client_config_with_local_server

    *   Mock MongoDB client - see usage of: mock_mongo_client

    *   Simple selection of test data - see usage of: set_service_test_data_filter

    """

    run_mode: RunMode = RunMode.CompletionMode

    command_line: str = ""
    _command_line_is_set: bool = False

    command_args: list[str] = field(default_factory = lambda: [])
    _command_args_are_set: bool = False

    cursor_cpos: int = 0
    comp_type: CompType = CompType.PrefixShown
    comp_key: int = 0

    _mock_client_input: bool = True

    file_mock: OpenFileMock = OpenFileMock({})

    client_config_dict: dict = field(default_factory = lambda: load_relay_demo_client_config_dict())
    mock_client_config_file_read: bool = True
    is_client_config_with_local_server: bool = True

    server_config_dict: dict = field(default_factory = lambda: load_relay_demo_server_config_dict())
    mock_server_config_file_read: bool = True
    is_server_config_with_mongo_start: bool = False
    enable_demo_git_loader: bool = False

    actual_stdout = None
    capture_stdout: bool = False

    actual_stderr = None
    capture_stderr: bool = False

    mock_mongo_client: bool = True

    assert_on_close: bool = True

    service_test_data_filter = [
        "TD_70_69_38_46",  # no data
    ]

    def set_run_mode(self, run_mode: RunMode):
        self.run_mode = run_mode
        return self

    def set_command_line(self, command_line: str):
        """
        Used as input for `RunMode.CompletionMode` because `COMP_LINE` is env var what Bash sets
        """
        self.command_line = command_line
        self.cursor_cpos = len(self.command_line)
        self._command_line_is_set = True
        return self

    def set_command_args(self, command_args: list[str]):
        """
        Used as input for `RunMode.InvocationMode` because list[str] is what `sys.argv` provides
        """
        self.command_args = command_args
        self._command_args_are_set = True
        return self

    def set_cursor_cpos(self, cursor_cpos: int):
        self.cursor_cpos = cursor_cpos
        return self

    def set_comp_type(self, comp_type: CompType):
        self.comp_type = comp_type
        return self

    def set_comp_key(self, comp_key: int):
        self.comp_key = comp_key
        return self

    def set_mock_client_input(self, given_val: bool):
        self._mock_client_input = given_val
        return self

    def set_client_config_dict(self, client_config: dict):
        self.client_config_dict = client_config
        return self

    def get_client_config_json(self):
        return json.dump(self.client_config_dict)

    def set_mock_client_config_file_read(self, given_val: bool):
        self.mock_client_config_file_read = given_val
        return self

    def set_client_config_with_local_server(self, given_val: bool):
        self.is_client_config_with_local_server = given_val
        return self

    def set_server_config_dict(self, server_config: dict):
        self.server_config_dict = server_config
        return self

    def get_server_config_yaml(self):
        return yaml.dump(self.server_config_dict)

    def set_mock_server_config_file_read(self, given_val: bool):
        self.mock_server_config_file_read = given_val
        return self

    def set_server_config_with_mongo_start(self, given_val: bool):
        self.is_server_config_with_mongo_start = given_val
        return self

    def set_enable_demo_git_loader(self, given_val: bool):
        self.enable_demo_git_loader = given_val
        return self

    def set_capture_stdout(self, given_val: bool):
        self.capture_stdout = given_val
        return self

    def set_capture_stderr(self, given_val: bool):
        self.capture_stderr = given_val
        return self

    def set_mock_mongo_client(self, mock_mongo_client: bool):
        self.mock_mongo_client = mock_mongo_client
        return self

    def set_service_test_data_filter(self, service_test_data_filter: list[str]):
        self.service_test_data_filter = service_test_data_filter
        return self

    @contextlib.contextmanager
    def mock_file_open(self):
        with mock.patch("builtins.open", self.file_mock.open) as file_mock:
            yield file_mock

    @contextlib.contextmanager
    def build(self):
        """
        Mock resources via "Combining Multiple Context Managers":
        https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html#combining-multiple-context-managers

        Warning:
            The approach below works in tests for setting up and tearing down mocks (judging by behavior),
            but there is no guarantee it is robust under all scenarios.
            For real resource management (when various exceptions raised), it has to be thoroughly tested.
        """

        # Ensure there are no false expectations if conflicting setup is done:
        assert not (self._command_line_is_set and self._command_args_are_set), "both cannot be true"

        if self.is_client_config_with_local_server:
            # So far, local server is only used for testing (which implies using mocked client config file access).
            # If fails here, for consistency, either enable client config file mocking or disable local server.
            assert self.mock_client_config_file_read

        if self.is_server_config_with_mongo_start:
            assert self.mock_server_config_file_read

        if self.enable_demo_git_loader:
            assert self.mock_client_config_file_read

        if self.mock_client_config_file_read:
            self.client_config_dict[use_local_requests_] = self.is_client_config_with_local_server
            self.file_mock.path_to_data[client_config_desc.default_file_path] = json.dumps(self.client_config_dict)

        if self.mock_server_config_file_read:
            self.server_config_dict[mongo_config_][mongo_server_][
                start_server_
            ] = self.is_server_config_with_mongo_start
            plugin_entry = self.server_config_dict[plugin_dict_][GitRepoLoader.__name__]
            plugin_entry[plugin_config_][is_plugin_enabled_] = self.enable_demo_git_loader

            plugin_entry = self.server_config_dict[plugin_dict_][ServiceLoader.__name__]
            plugin_entry[plugin_config_][test_data_ids_to_load_] = self.service_test_data_filter

            self.file_mock.path_to_data[server_config_desc.default_file_path] = yaml.dump(self.server_config_dict)

        with ExitStack() as exit_stack:

            # noinspection PyListCreation
            yield_list = []

            # Always mock file access - whether file data or mocked data is given depends on the config:
            yield_list.append(exit_stack.enter_context(self.mock_file_open()))

            if (
                self.mock_mongo_client
                and
                # If `mongomock` is already used, no need to mock MongoDB:
                not self.server_config_dict[mongo_config_][use_mongomock_only_]
            ):
                yield_list.append(exit_stack.enter_context(_mongo_client_mock_manager()))

            if self._mock_client_input:
                if self.run_mode == RunMode.CompletionMode:
                    yield_list.append(exit_stack.enter_context(
                        _mock_client_input_in_completion_mode(
                            self.command_line,
                            self.cursor_cpos,
                            self.comp_type,
                        )
                    ))
                elif self.run_mode == RunMode.InvocationMode:
                    if self._command_args_are_set:
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_invocation_mode_with_args(
                                self.command_args,
                            )
                        ))
                    else:
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_invocation_mode_with_line(
                                self.command_line,
                            )
                        ))
                else:
                    raise RuntimeError

            if self.capture_stdout:
                self.actual_stdout = io.StringIO()
                yield_list.append(exit_stack.enter_context(_mock_stdout(self.actual_stdout)))

            if self.capture_stderr:
                self.actual_stderr = io.StringIO()
                yield_list.append(exit_stack.enter_context(_mock_stderr(self.actual_stderr)))

            if self.assert_on_close:
                yield_list.append(exit_stack.enter_context(self.assert_all_cm()))

            yield yield_list

    @contextlib.contextmanager
    def assert_all_cm(self):
        try:
            yield
        finally:
            if self.mock_client_config_file_read:
                self.assert_client_config_read()
            if self.mock_server_config_file_read:
                self.assert_server_config_read()

    def assert_client_config_read(self):
        self.assert_file_read(client_config_desc.default_file_path)

    def assert_server_config_read(self):
        self.assert_file_read(server_config_desc.default_file_path)

    def assert_file_read(self, file_path: str):
        """
        Ensures that mocked file was actually accessed.

        If fails here, it means either/or:
        *   test setup was over-mocked (e.g. see `mock_server_config_file_read`, `mock_client_config_file_read`)
        *   test did not hit functionality that is supposed to access the file
        """
        self.file_mock.path_to_mock[file_path].assert_called_with(file_path)


@contextlib.contextmanager
def _mongo_client_mock_manager():
    get_mongo_client_orig = MongoClientWrapper.get_mongo_client
    target_name = get_mongo_client_orig.__module__ + "." + get_mongo_client_orig.__name__
    with mock.patch(target_name) as get_mongo_client_mock:
        get_mongo_client_mock.return_value = mongomock.MongoClient()
        yield get_mongo_client_mock


@contextlib.contextmanager
def _mock_client_input_in_completion_mode(command_line: str, cursor_cpos: int, comp_type: CompType):
    with mock.patch.dict(os.environ, {
        "COMP_LINE": command_line,
        "COMP_POINT": str(cursor_cpos),
        "COMP_TYPE": str(comp_type.value),
        "COMP_KEY": str(0),
    }) as env_mock:
        yield env_mock


@contextlib.contextmanager
def _mock_client_input_in_invocation_mode_with_line(command_line: str):
    command_args = re.compile(SpecialChar.TokenDelimiter.value).split(command_line)
    with mock.patch.object(sys, "argv", command_args) as argv_mock:
        yield argv_mock


@contextlib.contextmanager
def _mock_client_input_in_invocation_mode_with_args(command_args: list[str]):
    with mock.patch.object(sys, "argv", command_args) as argv_mock:
        yield argv_mock


@contextlib.contextmanager
def _mock_stdout(stdout_f):
    with contextlib.redirect_stdout(stdout_f) as stdout_mock:
        yield stdout_mock


@contextlib.contextmanager
def _mock_stderr(stderr_f):
    with contextlib.redirect_stderr(stderr_f) as stderr_mock:
        yield stderr_mock


def load_relay_demo_server_config_dict() -> dict:
    test_server_config_path = _get_resource_path("relay_demo/argrelay.server.yaml")
    with open(test_server_config_path) as f:
        server_config_dict = yaml.safe_load(f)
    return server_config_dict


def load_relay_demo_client_config_dict() -> dict:
    test_client_config_path = _get_resource_path("relay_demo/argrelay.client.json")
    with open(test_client_config_path) as f:
        client_config_dict = json.load(f)
    return client_config_dict


def _get_resource_path(rel_path: str):
    # Composing path to resource this way keeps its base directory always at this relative path:
    test_server_config_path = pkg_resources.resource_filename(argrelay.__name__, rel_path)
    return test_server_config_path


def default_test_parsed_context(command_line: str, cursor_cpos: int) -> ParsedContext:
    return ParsedContext.from_instance(
        default_test_input_context(command_line, cursor_cpos),
    )


def default_test_input_context(command_line: str, cursor_cpos: int) -> InputContext:
    return InputContext(
        command_line = command_line,
        cursor_cpos = cursor_cpos,
        comp_type = CompType.PrefixShown,
        is_debug_enabled = False,
        run_mode = RunMode.CompletionMode,
        comp_key = str(0),
    )
