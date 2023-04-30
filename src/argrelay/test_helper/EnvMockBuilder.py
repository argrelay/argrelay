"""
Mock environment (env vars, command line args, file access, database, etc.) for `argrelay` client or server
"""

from __future__ import annotations

import contextlib
import dataclasses
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
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.GitRepoLoaderConfigSchema import is_plugin_enabled_
from argrelay.custom_integ.ServiceLoader import ServiceLoader
from argrelay.custom_integ.ServiceLoaderConfigSchema import test_data_ids_to_load_
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.mongo_data import MongoClientWrapper
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.schema_config_core_client.ClientConfigSchema import use_local_requests_, client_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_server_, use_mongomock_only_
from argrelay.schema_config_core_server.MongoServerConfigSchema import start_server_
from argrelay.schema_config_core_server.QueryCacheConfigSchema import enable_query_cache_
from argrelay.schema_config_core_server.ServerConfigSchema import (
    mongo_config_,
    server_config_desc,
    plugin_dict_,
    query_cache_config_,
)
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_helper.OpenFileMock import OpenFileMock


@dataclass
class EnvMockBuilder:
    """
    All-in-one mock support which sets up the mocks and cleans them up as Python's Context Manager.

    For example:

    *   Mock env vars or `sys.argv` used by Bash to communicate input to argrelay client - see usage of:

        *   `_mock_client_input_in_completion_mode`
        *   `_mock_client_input_in_invocation_mode_with_args`
        *   `_mock_client_input_in_invocation_mode_with_line`

    *   Mock server and client config files - see usage of:

        *   `set_server_config_dict`
        *   `set_client_config_dict`

    *   Capture `stdout` and `stderr` - see usage of:

        *   `set_capture_stdout`
        *   `set_capture_stderr`

    *   Whether client uses `LocalClient`/`LocalServer` or `RemoteClient` with `CustomFlaskApp` - see usage of:

        *   `set_client_config_with_local_server`

    *   Mock MongoDB client - see usage of: `mock_mongo_client`

    *   Simple selection of test data - see usage of: `set_test_data_ids_to_load`

    *   Verifying plugin `InvocationInput` - see usage of: `delegator_plugin_invoke_action_func_path`

    *   ...

    """

    run_mode: RunMode = RunMode.CompletionMode

    command_line: str = ""
    _command_line_is_set: bool = False

    command_args: list[str] = field(default_factory = lambda: [])
    _command_args_are_set: bool = False

    cursor_cpos: int = -1
    _cursor_cpos_is_set: bool = False

    comp_type: CompType = CompType.PrefixShown
    comp_key: int = 0

    _mock_client_input: bool = True

    file_mock: OpenFileMock = OpenFileMock({})

    client_config_dict: dict = field(default_factory = lambda: load_custom_integ_client_config_dict())
    mock_client_config_file_read: bool = True
    is_client_config_with_local_server: bool = True

    server_config_dict: dict = field(default_factory = lambda: load_custom_integ_server_config_dict())
    mock_server_config_file_read: bool = True
    is_server_config_with_mongo_start: bool = False
    enable_demo_git_loader: bool = False

    actual_stdout = None
    capture_stdout: bool = False

    actual_stderr = None
    capture_stderr: bool = False

    mock_mongo_client: bool = True

    assert_on_close: bool = True

    test_data_ids_to_load = [
        "TD_70_69_38_46",  # no data
    ]

    delegator_plugin_invoke_action_func_path = None
    invocation_input: InvocationInput = None

    enable_query_cache: bool = True

    def set_run_mode(self, run_mode: RunMode):
        self.run_mode = run_mode
        return self

    def set_command_line(self, command_line: str):
        """
        Used as input for `RunMode.CompletionMode` because `COMP_LINE` is env var what Bash sets
        """
        self.command_line = command_line
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
        self._cursor_cpos_is_set = True
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

    def set_test_data_ids_to_load(self, test_data_ids_to_load: list[str]):
        self.test_data_ids_to_load = test_data_ids_to_load
        return self

    def set_capture_delegator_invocation_input(self, abstract_delegator: AbstractDelegator):
        """
        This func causes `AbstractDelegator.invoke_action` to be mocked to capture `InvocationInput`
        inside `ErrorDelegator.invocation_input` which test can then assert its data.
        """

        self.delegator_plugin_invoke_action_func_path = (
            f"{abstract_delegator.__module__}"
            "."
            f"{abstract_delegator.__name__}"
            "."
            "invoke_action"
        )
        return self

    def set_enable_query_cache(self, given_val: bool):
        self.enable_query_cache = given_val
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

        if self._command_line_is_set:
            assert self._cursor_cpos_is_set, "setting command line (in CompletionMode) requires cursor cpos"

        if self._command_args_are_set:
            assert not self._cursor_cpos_is_set, "if args are set (in InvocationMode), cursor pos is not set"

        if self.is_client_config_with_local_server:
            # So far, local server is only used for testing (which implies using mocked client config file access).
            # If fails here, for consistency, either enable client config file mocking or disable local server.
            assert self.mock_client_config_file_read

        if self.is_server_config_with_mongo_start:
            assert self.mock_server_config_file_read

        if self.enable_demo_git_loader:
            assert self.mock_client_config_file_read

        if self.enable_query_cache != self.server_config_dict[query_cache_config_][enable_query_cache_]:
            assert self.mock_server_config_file_read

        if self.mock_client_config_file_read:
            self.client_config_dict[use_local_requests_] = self.is_client_config_with_local_server
            self.file_mock.path_to_data[client_config_desc.default_file_path] = json.dumps(self.client_config_dict)

        if self.mock_server_config_file_read:
            """
            Change server config data, then mock file access to return that data for tests.
            """

            self.server_config_dict[mongo_config_][mongo_server_][
                start_server_
            ] = self.is_server_config_with_mongo_start
            plugin_entry = self.server_config_dict[plugin_dict_][GitRepoLoader.__name__]
            plugin_entry[plugin_config_][is_plugin_enabled_] = self.enable_demo_git_loader

            plugin_entry = self.server_config_dict[plugin_dict_][ServiceLoader.__name__]
            plugin_entry[plugin_config_][test_data_ids_to_load_] = self.test_data_ids_to_load

            self.server_config_dict[query_cache_config_][enable_query_cache_] = self.enable_query_cache

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
                    # TODO: make explicit function "mock_client_input_on_CompletionMode" with all three args required.
                    yield_list.append(exit_stack.enter_context(
                        _mock_client_input_in_completion_mode(
                            self.command_line,
                            self.cursor_cpos,
                            self.comp_type,
                        )
                    ))
                elif self.run_mode == RunMode.InvocationMode:
                    # TODO: make explicit function "mock_client_input_on_InvocationMode" with just command_args.
                    if self._command_args_are_set:
                        # TODO: do not branch here, branch on mock setup (in client tests) to make it explicit/conscious that InvocationMode is not about command_line, but command_args.
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_invocation_mode_with_args(
                                self.command_args,
                            )
                        ))
                    elif self._command_line_is_set:
                        # TODO: do not branch here, branch on mock setup (in client tests) to make it explicit/conscious that InvocationMode is not about command_line, but command_args.
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_invocation_mode_with_line(
                                self.command_line,
                            )
                        ))
                    else:
                        raise RuntimeError
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

            if self.delegator_plugin_invoke_action_func_path:
                yield_list.append(exit_stack.enter_context(
                    _mock_delegator_plugin(self.delegator_plugin_invoke_action_func_path)
                ))

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


@dataclass
class ServerOnlyEnvMockBuilder(EnvMockBuilder):
    """
    Used in tests where client code is not invoked.
    """

    def __init__(
        self,
    ):
        super().__init__()
        # TODO: enable validation that client code is not invoked:
        # For server-only test, client config file read should not happen.
        # Disable expectations:
        self.set_mock_client_config_file_read(False)
        # For server-only test, client code is not used, but if it is, try to fail via REST API:
        self.set_client_config_with_local_server(False)
        # For server-only test, client input mocking is not required:
        self.set_mock_client_input(False)


@dataclass
class LiveServerEnvMockBuilder(EnvMockBuilder):
    """
    Used in tests where client talks to some live server.

    The purpose of this mock is to test server data (rather than code).
    """

    def __init__(
        self,
    ):
        super().__init__()
        # TODO: enable validation that client code is not invoked:
        # For live server test, server config file read should not happen by in-process server code.
        # Disable expectations:
        self.set_mock_server_config_file_read(False)
        # For live server test, running local server contradicts with the purpose:
        self.set_client_config_with_local_server(False)


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


def _mock_client_input_in_invocation_mode_with_line(command_line: str):
    command_args = re.compile(SpecialChar.TokenDelimiter.value).split(command_line)
    return _mock_client_input_in_invocation_mode_with_args(command_args)


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


@contextlib.contextmanager
def _mock_delegator_plugin(path_to_invoke_action):
    with mock.patch(path_to_invoke_action, capture_invocation_input) as mock_static:
        yield mock_static


def capture_invocation_input(invocation_input: InvocationInput):
    """
    This body substitutes (mocks) `invoke_action` func in `DelegatorPlugin`-s.

    Instead of executing func logic, it only captures its input for verifications in tests.
    """
    EnvMockBuilder.invocation_input = dataclasses.replace(invocation_input)


def load_custom_integ_server_config_dict() -> dict:
    test_server_config_path = _get_resource_path("sample_conf/argrelay.server.yaml")
    with open(test_server_config_path) as f:
        server_config_dict = yaml.safe_load(f)
    return server_config_dict


def load_custom_integ_client_config_dict() -> dict:
    test_client_config_path = _get_resource_path("sample_conf/argrelay.client.json")
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
