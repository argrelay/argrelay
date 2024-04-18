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
import tempfile
from contextlib import ExitStack
from dataclasses import dataclass, field
from io import StringIO
from typing import Type, Union, Callable
from unittest import mock

import yaml

from argrelay.client_spec.ShellContext import (
    UNKNOWN_COMP_KEY,
    ShellContext,
    COMP_LINE_env_var,
    COMP_POINT_env_var,
    COMP_TYPE_env_var,
    COMP_KEY_env_var,
)
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.ServiceLoader import ServiceLoader
from argrelay.custom_integ.ServiceLoaderConfigSchema import test_data_ids_to_load_
from argrelay.enum_desc.CallConv import CallConv
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.schema_config_core_client.ClientConfigSchema import (
    use_local_requests_,
    client_config_desc,
    optimize_completion_request_,
    show_pending_spinner_,
)
from argrelay.schema_config_core_server.MongoConfigSchema import (
    use_mongomock_,
    distinct_values_query_,
)
from argrelay.schema_config_core_server.QueryCacheConfigSchema import enable_query_cache_
from argrelay.schema_config_core_server.ServerConfigSchema import (
    mongo_config_,
    server_config_desc,
    plugin_instance_entries_,
    query_cache_config_,
)
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_, plugin_enabled_
from argrelay.schema_response.InvocationInput import InvocationInput
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_infra.LocalClientCommandFactory import LocalClientCommandFactory
from argrelay.test_infra.OpenFileMock import OpenFileMock
from argrelay.test_infra.PopenMock import PopenMock


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

    *   Mock MongoDB client - see usage of: `use_mongomock`

    *   Simple selection of test data - see usage of: `set_test_data_ids_to_load`

    *   TODO_42_81_01_90: Verify `ArgValues` on `ServerAction.DescribeLineArgs` (without verifying printed output) by intercepting call to `ProposeArgValuesClientResponseHandler.render_values`.
    *   TODO_42_81_01_90: Verify `InterpResult` on `ServerAction.ProposeArgValues` (without verifying printed output) by intercepting call to `DescribeLineArgsClientResponseHandler.render_result`.
    *   Verifying `InvocationInput` on `ServerAction.RelayLineArgs` - see usage of:

        *   `invoke_action_func_full_name`

    *   ...

    """

    ####################################################################################################################
    # Client input

    command_line: Union[str, None] = field(default = None)
    command_args: Union[list[str], None] = field(default = None)
    cursor_cpos: Union[int, None] = field(default = None)
    comp_type: Union[CompType, None] = field(default = None)
    # The `comp_key` value is not used at the moment (but it is provided by shell in case of `CallConv.EnvVarsConv`) -
    # using any default value for now to avoid setting it everywhere
    # (when it starts to matter, change default to `None` to force review and specifying it in all tests):
    comp_key: str = field(default = UNKNOWN_COMP_KEY)

    # TODO: Keep default to False (to do the minimum by default) - one has to select pre-set builder class to get defaults instead:
    _mock_client_input: bool = field(default = True)

    ####################################################################################################################
    # Client config

    is_client_config_with_local_server: bool = field(default = True)
    is_client_config_to_optimize_completion_request: bool = field(default = None)
    show_pending_spinner: Union[bool, None] = field(default = False)

    ####################################################################################################################
    # Server config

    test_data_ids_to_load: list[str] = field(default_factory = lambda: [
        "TD_70_69_38_46",  # no data
    ])

    enable_demo_git_loader: bool = field(default = False)
    use_mongomock: Union[bool, None] = field(default = None)

    enable_query_cache: Union[bool, None] = field(default = None)
    """
    See `QueryCacheConfig.enable_query_cache`.
    """

    distinct_values_query: Union[DistinctValuesQuery, None] = field(default = None)
    """
    See `DistinctValuesQuery`.
    """

    ####################################################################################################################
    # Output capturing

    actual_stdout: StringIO = field(default = None)
    capture_stdout: bool = field(default = False)

    actual_stderr: StringIO = field(default = None)
    capture_stderr: bool = field(default = False)

    ####################################################################################################################
    # Config file mocking

    client_config_dict: Union[dict, None] = field(default_factory = lambda: None)
    server_config_dict: Union[dict, None] = field(default_factory = lambda: None)

    mock_client_config_file_read: bool = field(default = False)
    mock_server_config_file_read: bool = field(default = False)

    # Implement FS_62_25_92_06 generated config for `out`-processes to read it (see FS_66_17_43_42 test infra):
    generate_client_config_file: bool = field(default = False)
    generate_server_config_file: bool = field(default = False)
    temp_test_config_dir: Union[tempfile.TemporaryDirectory, None] = None

    ####################################################################################################################
    # General mocking

    file_mock: OpenFileMock = field(default_factory = lambda: OpenFileMock({}))

    assert_on_close: bool = field(default = True)

    ####################################################################################################################
    # Intercept specific payload

    invoke_action_func_full_name: str = field(default = None)
    """
    Set by giving `delegator_class` to `set_capture_delegator_invocation_input`.
    """
    invocation_input: InvocationInput = field(default = None)
    """
    Captured `InvocationInput` by using `capture_invocation_input` func on `ServerAction.RelayLineArgs`
    instead of calling client-side delegator.
    """

    ####################################################################################################################
    # Server control

    reset_local_server: bool = field(default = True)
    """
    If true, (after build() context is over) next invocation via `LocalClient` will trigger `LocalServer` restart (re-creation and re-load).
    Default is true because it is confusing to hold `test_data_ids_to_load` while not re-loading server by default.
    """

    was_server_started_on_build: bool = field(default = False)
    """
    Avoids triggering verification of file access mock usage for server config
    when `LocalClient` reuses already running server.
    See FS_66_17_43_42 test infra for server-`out` test modes.
    """

    ####################################################################################################################
    # Client input

    def set_command_line(self, command_line: str):
        """
        Used as input in case of `CallConv.CliArgsConv` because `COMP_LINE` is env var what Bash sets
        """
        self.command_line = command_line
        return self

    def set_command_args(self, command_args: list[str]):
        """
        Used as input in case of `CallConv.EnvVarsConv` because list[str] is what `sys.argv` provides
        """
        self.command_args = command_args
        return self

    def set_cursor_cpos(self, cursor_cpos: int):
        self.cursor_cpos = cursor_cpos
        return self

    def set_comp_type(self, comp_type: CompType):
        self.comp_type = comp_type
        return self

    def set_comp_key(self, comp_key: str):
        self.comp_key = comp_key
        return self

    def set_mock_client_input(self, given_val: bool):
        self._mock_client_input = given_val
        return self

    ####################################################################################################################
    # Client config

    def set_client_config_with_local_server(self, given_val: bool):
        self.is_client_config_with_local_server = given_val
        return self

    def set_client_config_to_optimize_completion_request(self, given_val: Union[bool, None]):
        self.is_client_config_to_optimize_completion_request = given_val
        return self

    def set_show_pending_spinner(
        self,
        given_val: Union[bool, None],
    ):
        self.show_pending_spinner = given_val
        return self

    ####################################################################################################################
    # Server config

    def set_test_data_ids_to_load(self, test_data_ids_to_load: list[str]):
        self.test_data_ids_to_load = test_data_ids_to_load
        return self

    def set_enable_demo_git_loader(self, given_val: bool):
        self.enable_demo_git_loader = given_val
        return self

    def set_use_mongomock(
        self,
        given_val: Union[bool, None],
    ):
        self.use_mongomock = given_val
        return self

    def set_enable_query_cache(
        self,
        given_val: Union[bool, None],
    ):
        self.enable_query_cache = given_val
        return self

    def set_distinct_values_query(
        self,
        distinct_values_query: Union[distinct_values_query, None]
    ):
        self.distinct_values_query = distinct_values_query
        return self

    ####################################################################################################################
    # Output capturing

    def set_capture_stdout(self, given_val: bool):
        self.capture_stdout = given_val
        return self

    def set_capture_stderr(self, given_val: bool):
        self.capture_stderr = given_val
        return self

    ####################################################################################################################
    # Config file mocking

    def set_client_config_dict(
        self,
        client_config: Union[dict, None] = None,
    ):
        if client_config is None:
            client_config = client_config_desc.dict_from_default_file()
        self.client_config_dict = client_config
        return self

    def set_server_config_dict(
        self,
        server_config: Union[dict, None] = None,
    ):
        if server_config is None:
            server_config = server_config_desc.dict_from_default_file()
        self.server_config_dict = server_config
        return self

    def get_client_config_json(self):
        return json.dump(self.client_config_dict)

    def get_server_config_yaml(self):
        return yaml.dump(self.server_config_dict)

    def set_mock_client_config_file_read(self, given_val: bool):
        self.mock_client_config_file_read = given_val
        return self

    def set_mock_server_config_file_read(self, given_val: bool):
        self.mock_server_config_file_read = given_val
        return self

    def set_generate_client_config_file(self, given_val: bool):
        self.generate_client_config_file = given_val
        return self

    def set_generate_server_config_file(self, given_val: bool):
        self.generate_server_config_file = given_val
        return self

    ####################################################################################################################
    # General mocking

    @contextlib.contextmanager
    def mock_file_open(self):
        with mock.patch("builtins.open", self.file_mock.open) as file_mock:
            yield file_mock

    ####################################################################################################################
    # Intercept specific payload

    def set_capture_delegator_invocation_input(self, delegator_class: Type[AbstractDelegator]):
        """
        This func causes `AbstractDelegator.invoke_action` to be mocked to capture `InvocationInput`
        inside `EnvMockBuilder.invocation_input` allowing tests to assert
        the data received from server on `ServerAction.RelayLineArgs`.
        """

        self.invoke_action_func_full_name = (
            f"{delegator_class.__module__}"
            "."
            f"{delegator_class.__name__}"
            "."
            "invoke_action"
        )
        return self

    ####################################################################################################################
    # Server control

    def set_reset_local_server(self, given_val: bool):
        self.reset_local_server = given_val
        return self

    ####################################################################################################################

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

        ################################################################################################################
        # Initial validation

        self.was_server_started_on_build = LocalClientCommandFactory.local_server is not None

        # Ensure there are no false expectations if conflicting setup is done:
        assert self.command_line is None or self.command_args is None, "both cannot be set, at most one"

        if self.command_line is not None:
            assert self.cursor_cpos is not None, "setting command line (in CompletionMode) requires setting cursor cpos"

        if self.command_args is not None:
            assert self.cursor_cpos is None, "if args are set (in InvocationMode), cursor pos should not be set"

        self.assert_config_substitution_mutually_exclusive()

        ################################################################################################################
        # Client config

        if self.client_config_dict is not None:
            self.assert_client_config_substitute_enabled()

        if self.is_client_config_with_local_server:
            # So far, local client is only used for testing (which implies using mocked client config file access).
            # If fails here, for consistency, either enable client config file mocking or disable local client.
            self.assert_client_config_substitute_enabled()

        if self.is_client_config_to_optimize_completion_request is not None:
            self.assert_client_config_substitute_enabled()

        if self.show_pending_spinner is not None:
            self.assert_client_config_substitute_enabled()

        ################################################################################################################
        # Server config

        if self.server_config_dict is not None:
            self.assert_server_config_substitute_enabled()

        if self.enable_demo_git_loader:
            self.assert_server_config_substitute_enabled()

        if self.enable_query_cache is not None:
            self.assert_server_config_substitute_enabled()

        if self.distinct_values_query is not None:
            self.assert_server_config_substitute_enabled()

        if self.use_mongomock is not None:
            self.assert_server_config_substitute_enabled()

        ################################################################################################################

        if self.mock_client_config_file_read or self.generate_client_config_file:

            assert self.client_config_dict is not None

            self.client_config_dict[use_local_requests_] = self.is_client_config_with_local_server

            if self.is_client_config_to_optimize_completion_request is not None:
                self.client_config_dict[
                    optimize_completion_request_
                ] = self.is_client_config_to_optimize_completion_request

            if self.show_pending_spinner is not None:
                self.client_config_dict[
                    show_pending_spinner_
                ] = self.show_pending_spinner

            # set mocked file content:
            if self.mock_client_config_file_read:
                self.file_mock.path_to_data[client_config_desc.get_adjusted_file_path()] = json.dumps(
                    self.client_config_dict
                )

        if self.mock_server_config_file_read or self.generate_server_config_file:
            """
            Change server config data, then mock file access to return that data for tests.
            """
            assert self.server_config_dict is not None

            # TODO: Do not hardcode plugin id (instance of `GitRepoLoader`):
            plugin_entry = self.server_config_dict[plugin_instance_entries_][f"{GitRepoLoader.__name__}.default"]
            plugin_entry[plugin_enabled_] = self.enable_demo_git_loader

            # TODO: Do not hardcode plugin id (instance of `ServiceLoader`):
            plugin_entry = self.server_config_dict[plugin_instance_entries_][f"{ServiceLoader.__name__}.default"]
            plugin_entry[plugin_config_][test_data_ids_to_load_] = self.test_data_ids_to_load

            if self.enable_query_cache is not None:
                self.server_config_dict[query_cache_config_][enable_query_cache_] = self.enable_query_cache

            if self.distinct_values_query is not None:
                self.server_config_dict[mongo_config_][distinct_values_query_] = self.distinct_values_query.name

            if self.use_mongomock is not None:
                self.server_config_dict[mongo_config_][use_mongomock_] = self.use_mongomock

            # set mocked file content:
            if self.mock_server_config_file_read:
                self.file_mock.path_to_data[server_config_desc.get_adjusted_file_path()] = yaml.dump(
                    self.server_config_dict
                )

        with ExitStack() as exit_stack:

            # noinspection PyListCreation
            yield_list = []

            # Always mock file access - whether file data or mocked data is given depends on the mock config:
            yield_list.append(exit_stack.enter_context(self.mock_file_open()))

            if self._mock_client_input:

                assert self.comp_type is not None, "if mocking client input was requested, `comp_type` cannot be `None`"

                if CallConv.from_comp_type(self.comp_type) is CallConv.EnvVarsConv:
                    if self.command_line is not None and self.cursor_cpos is not None:
                        # TODO: make explicit function "mock_client_input_in_env_vars" with all three args required.
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_env_vars(
                                self.command_line,
                                self.cursor_cpos,
                                self.comp_type,
                            )
                        ))
                    else:
                        raise RuntimeError
                elif CallConv.from_comp_type(self.comp_type) is CallConv.CliArgsConv:
                    # TODO: make explicit function "mock_client_input_in_cli_args" with just command_args.
                    if self.command_args is not None:
                        # TODO: do not branch here, branch on mock setup (in client tests) to make it explicit/conscious that InvocationMode is not about command_line, but command_args.
                        yield_list.append(exit_stack.enter_context(
                            _mock_client_input_in_invocation_mode_with_args(
                                self.command_args,
                            )
                        ))
                    elif self.command_line is not None:
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
                yield_list.append(exit_stack.enter_context(_capture_stdout(self.actual_stdout)))

            if self.capture_stderr:
                self.actual_stderr = io.StringIO()
                yield_list.append(exit_stack.enter_context(_capture_stderr(self.actual_stderr)))

            if self.assert_on_close:
                yield_list.append(exit_stack.enter_context(self.assert_all_cm()))

            if self.invoke_action_func_full_name:
                yield_list.append(exit_stack.enter_context(
                    _mock_delegator_plugin(self.invoke_action_func_full_name)
                ))

            if self.reset_local_server:
                yield_list.append(exit_stack.enter_context(
                    do_reset_local_server()
                ))

            if (
                self.generate_client_config_file
                or
                self.generate_server_config_file
            ):
                yield_list.append(exit_stack.enter_context(
                    self.generate_configs()
                ))

            yield yield_list

    def assert_config_substitution_mutually_exclusive(self):
        assert (
            (
                self.mock_client_config_file_read == self.generate_client_config_file == False
                or
                self.mock_client_config_file_read != self.generate_client_config_file
            )
            and
            (
                self.mock_server_config_file_read == self.generate_server_config_file == False
                or
                self.mock_server_config_file_read != self.generate_server_config_file
            )
        ), "FS_62_25_92_06: generated config: mocked config and generated config are mutually exclusive"

    def assert_client_config_substitute_enabled(self):
        assert (
            self.mock_client_config_file_read
            or
            self.generate_client_config_file
        ), "FS_62_25_92_06: generated config: when enabled: either mocked config or generated config"

    def assert_server_config_substitute_enabled(self):
        assert (
            self.mock_server_config_file_read
            or
            self.generate_server_config_file
        ), "FS_62_25_92_06: generated config: when enabled: either mocked config or generated config"

    @contextlib.contextmanager
    def assert_all_cm(self):
        try:
            yield
        finally:
            if self.mock_client_config_file_read:
                self.assert_client_config_read()
            if self.mock_server_config_file_read and not self.was_server_started_on_build:
                self.assert_server_config_read()

    def assert_client_config_read(self):
        self.assert_file_read(client_config_desc.get_adjusted_file_path())

    def assert_server_config_read(self):
        self.assert_file_read(server_config_desc.get_adjusted_file_path())

    def assert_file_read(self, file_path: str):
        """
        Ensures that mocked file was actually accessed.

        If fails here, it means either/or:
        *   test setup was over-mocked (e.g. see `mock_server_config_file_read`, `mock_client_config_file_read`)
        *   test did not hit functionality that is supposed to access the file
        """
        self.file_mock.path_to_mock[file_path].assert_called_with(file_path)

    @contextlib.contextmanager
    def generate_configs(
        self,
    ):
        base_tmp_dir = f"{get_argrelay_dir()}/tmp"
        assert os.path.isdir(base_tmp_dir)

        test_configs_dir = f"{base_tmp_dir}/test_configs"
        if not os.path.exists(test_configs_dir):
            os.makedirs(test_configs_dir)

        self.temp_test_config_dir = tempfile.TemporaryDirectory(dir = f"{test_configs_dir}/")
        try:
            with self.temp_test_config_dir:
                os.environ["ARGRELAY_CONF_BASE_DIR"] = self.temp_test_config_dir.name
                self.inner_generate_configs()
                yield
        finally:
            os.environ.pop("ARGRELAY_CONF_BASE_DIR")

    def inner_generate_configs(self):
        client_config_path = os.path.join(
            self.temp_test_config_dir.name,
            client_config_desc.default_file_path,
        )
        server_config_path = os.path.join(
            self.temp_test_config_dir.name,
            server_config_desc.default_file_path,
        )
        if self.generate_client_config_file:
            self.generate_client_config(str(client_config_path))
        if self.generate_server_config_file:
            self.generate_server_config(str(server_config_path))

    def generate_client_config(
        self,
        file_path: str,
    ):
        with open(file_path, "w") as json_file:
            json.dump(
                self.client_config_dict,
                json_file,
            )

    def generate_server_config(
        self,
        file_path: str,
    ):
        with open(file_path, "w") as yaml_file:
            yaml.dump(
                self.server_config_dict,
                yaml_file,
            )


########################################################################################################################
# Pre-configured mock builders

@dataclass
class EmptyEnvMockBuilder(EnvMockBuilder):
    """
    Use case:
    Used to set up extra mocks before or after when nesting `EnvMockBuilder` one into another (or completely alone).
    Without calling any extra setters after creation to prime some mocks, this `EnvMockBuilder`  is noop.
    """

    def __init__(
        self,
    ):
        super().__init__()
        self.set_mock_client_input(False)
        self.set_reset_local_server(False)
        # Disable all mocks which set tripwires if not used:
        self.set_mock_client_config_file_read(False)
        self.set_mock_server_config_file_read(False)
        self.set_client_config_with_local_server(False)
        # Client config is not substituted but otherwise default `show_pending_spinner = False` requires it - use None:
        self.set_show_pending_spinner(None)


@dataclass
class LocalClientEnvMockBuilder(EnvMockBuilder):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #1.

    Use case:
    Used in tests where both server and client code is verified but without code for data marshalling via HTTP.
    Runs client and server code in the same test process via `LocalClient` (see for more details).
    """

    def __init__(
        self,
    ):
        super().__init__()

        # TODO: enable validation that client code is actually invoked (e.g. invocation of make_request in main):

        # Ensure that client and server read their config files by test process:
        self.set_mock_client_config_file_read(True)
        self.set_mock_server_config_file_read(True)
        self.set_generate_client_config_file(False)
        self.set_generate_server_config_file(False)

        # Load default configs as file access mocks input:
        self.set_client_config_dict()
        self.set_server_config_dict()

        # For local client (with local server) tests,
        # ensure client uses `LocalClient` without marshalling data via HTTP:
        self.set_client_config_with_local_server(True)
        # Also, ensure non-optimized completion is used
        # (optimized directly uses network socket which will not give access to `LocalServer`):
        self.set_client_config_to_optimize_completion_request(False)

        # For local client (with local server) tests,
        # client code will need to access data passed by the shell - mock it:
        self.set_mock_client_input(True)


@dataclass
class ServerOnlyEnvMockBuilder(EnvMockBuilder):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #7.

    Use case:
    Used in tests where client code is not invoked (or external to the test process like GUI).
    Current test process runs only server code - use this class to mock server environment (e.g. config).
    """

    def __init__(
        self,
    ):
        super().__init__()

        # TODO: enable validation that client code is not invoked (e.g. invocation of make_request):

        # For server-only test, client config file read should not happen by test process
        # (if this mock is enabled, but not used, it fails):
        self.set_mock_client_config_file_read(False)
        self.set_generate_client_config_file(False)

        # For server-only test, use mocked server config file access (to control its content in test):
        self.set_mock_server_config_file_read(True)
        self.set_generate_server_config_file(False)

        # Load default server config as file access mock input:
        self.set_server_config_dict()

        # For server-only test, client code is not used, but if it is, try to fail via REST API:
        self.set_client_config_with_local_server(False)

        # For server-only test, client input mocking is not required:
        self.set_mock_client_input(False)

        # Client config is not substituted but otherwise default `show_pending_spinner = False` requires it - use None:
        self.set_show_pending_spinner(None)


@dataclass
class LiveServerEnvMockBuilder(EnvMockBuilder):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #2.

    Use case:
    Used in tests where client talks to some live server.
    Server is started somehow outside the mock, current test process runs only client code.
    """

    def __init__(
        self,
    ):
        super().__init__()

        # TODO: enable validation that server code is not invoked (e.g. no invocation of create_call_ctx):

        # For live server test, do not substitute client config by default
        # (because default client config contains correct connection details for default live server):
        self.set_mock_client_config_file_read(False)
        self.set_generate_client_config_file(False)
        # Client config is not substituted but otherwise default `show_pending_spinner = False` requires it - use None:
        self.set_show_pending_spinner(None)

        # For live server test, server config file substitution should not happen by test process code
        # (because it happens within server process - un-verify-able from the test process):
        self.set_mock_server_config_file_read(False)
        self.set_generate_server_config_file(False)

        # For live server test, running local server contradicts with the live server - disable:
        self.set_client_config_with_local_server(False)
        # Optimized client prevents accessing internal server state via `LocalClient` and `LocalServer`,
        # but it is impossible with live server anyway.
        # Therefore, default is unspecified here = None
        # (whatever is set in the client config or dictated by its defaults):
        self.set_client_config_to_optimize_completion_request(None)


########################################################################################################################
# Client input mocking

@contextlib.contextmanager
def _mock_client_input_in_env_vars(command_line: str, cursor_cpos: int, comp_type: CompType):
    with mock.patch.dict(os.environ, {
        COMP_LINE_env_var: command_line,
        COMP_POINT_env_var: str(cursor_cpos),
        COMP_TYPE_env_var: str(comp_type.value),
        COMP_KEY_env_var: UNKNOWN_COMP_KEY,
    }) as env_mock:
        yield env_mock


def _mock_client_input_in_invocation_mode_with_line(command_line: str):
    command_args = re.compile(SpecialChar.TokenDelimiter.value).split(command_line)
    return _mock_client_input_in_invocation_mode_with_args(command_args)


@contextlib.contextmanager
def _mock_client_input_in_invocation_mode_with_args(command_args: list[str]):
    with mock.patch.object(sys, "argv", command_args) as argv_mock:
        yield argv_mock


########################################################################################################################
# Output capturing

@contextlib.contextmanager
def _capture_stdout(stdout_f):
    with contextlib.redirect_stdout(stdout_f) as stdout_mock:
        yield stdout_mock


@contextlib.contextmanager
def _capture_stderr(stderr_f):
    with contextlib.redirect_stderr(stderr_f) as stderr_mock:
        yield stderr_mock


########################################################################################################################
# Intercept specific payload

@contextlib.contextmanager
def _mock_delegator_plugin(path_to_invoke_action):
    with mock.patch(path_to_invoke_action, capture_invocation_input) as invoke_action_mock:
        yield invoke_action_mock


def capture_invocation_input(invocation_input: InvocationInput):
    """
    This body substitutes (mocks) `invoke_action` func in `DelegatorPlugin`-s.

    Instead of executing func logic, it only captures its `InvocationInput` for verifications in tests.
    """
    EnvMockBuilder.invocation_input = dataclasses.replace(invocation_input)


########################################################################################################################
# Stand-alone util mock funcs

@contextlib.contextmanager
def mock_subprocess_popen(expected_args_to_output):
    with mock.patch("subprocess.Popen", PopenMock(expected_args_to_output)) as popen_mock:
        yield popen_mock


@contextlib.contextmanager
def wrap_instance_method_on_instance(
    any_instance,
    callable_on_instance: Callable,
):
    """
    Wraps `callable_on_instance` by a mock which still calls original method.
    Use case: test whether original method is called.
    See also: `wrap_instance_method_on_class` - similar purpose but requires completely different mocking call.
    """
    with mock.patch.object(
        any_instance,
        callable_on_instance.__name__,
        wraps = callable_on_instance,
    ) as method_wrap_mock:
        yield method_wrap_mock


@contextlib.contextmanager
def wrap_instance_method_on_class(
    any_class,
    callable_on_instance: Callable,
):
    """
    Wraps `callable_on_instance` by a mock which still calls original method.
    Use case: test whether original method is called.
    See also: `wrap_instance_method_on_instance` - similar purpose but requires completely different mocking call.
    """
    with mock.patch(
        f"{any_class.__module__}.{any_class.__name__}.{callable_on_instance.__name__}",
        side_effect = callable_on_instance,
        autospec = True,
    ) as method_wrap_mock:
        yield method_wrap_mock


@contextlib.contextmanager
def do_reset_local_server():
    try:
        yield
    finally:
        LocalClientCommandFactory.local_server = None


########################################################################################################################
# Test objects

def default_test_parsed_context(
    command_line: str,
    cursor_cpos: int,
    comp_type: CompType = CompType.PrefixShown,
) -> ParsedContext:
    return ParsedContext.from_instance(
        default_test_call_context(
            command_line,
            cursor_cpos,
            comp_type,
        ),
    )


def default_test_call_context(
    command_line: str,
    cursor_cpos: int,
    comp_type: CompType = CompType.PrefixShown,
) -> CallContext:
    return ShellContext(
        command_line = command_line,
        cursor_cpos = cursor_cpos,
        comp_type = comp_type,
        comp_key = UNKNOWN_COMP_KEY,
        is_debug_enabled = False,
    ).create_call_context()
