from __future__ import annotations

import os

from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_command_remote.exception_utils import ServerResponseError
from argrelay.client_pipeline import BytesSrcAbstract
from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.TopDir import TopDir
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.server_spec.CallContext import CallContext

server_index_file_name = "argrelay_client.server_index"
random_file = "/dev/random"


def get_var_dir_path() -> str:
    return str(os.path.join(get_argrelay_dir(), TopDir.var_dir.value))


def get_server_index_file_path() -> str:
    return str(os.path.join(get_var_dir_path(), server_index_file_name))


def load_server_index(
) -> int:
    server_index_file_path = get_server_index_file_path()
    if os.path.isfile(server_index_file_path):
        with open(server_index_file_path, "r") as open_file:
            return int(open_file.read())
    else:
        with open(random_file, "rb") as open_file:
            return int.from_bytes(open_file.read(1), "little")


def store_server_index(
    curr_server_index: int,
) -> None:
    os.makedirs(
        get_var_dir_path(),
        exist_ok = True,
    )
    server_index_file_path = get_server_index_file_path()
    with open(server_index_file_path, "w") as open_file:
        open_file.write(str(curr_server_index))


class ClientCommandRemoteWorkerAbstract(ClientCommandRemoteAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        proc_role: ProcRole,
        redundant_servers: list[ConnectionConfig],
        server_index: int,
        bytes_src: BytesSrcAbstract,
    ):
        super().__init__(
            call_ctx,
            proc_role,
        )
        self.redundant_servers: list[ConnectionConfig] = redundant_servers
        self.bytes_src: BytesSrcAbstract = bytes_src
        if server_index < 0:
            self.curr_connection_config: ConnectionConfig = self.redundant_servers[0]
            self.use_round_robin = True
        else:
            self.curr_connection_config: ConnectionConfig = self.redundant_servers[server_index]
            self.use_round_robin = False

        self.server_index_file_path: str = get_server_index_file_path()

    def execute_command(
        self,
    ):
        if not self.use_round_robin:
            self._execute_single_call()
        else:
            self._execute_multiple_calls()

    def _execute_multiple_calls(
        self,
    ):
        """
        Implements FS_93_18_57_91 client fail over.

        For basic implementation (no round-robin) see base `ClientCommandRemoteAbstract` class.
        """
        connections_count = len(self.redundant_servers)
        init_server_index = load_server_index()
        for curr_connection_offset in range(connections_count):
            curr_server_index = (init_server_index + curr_connection_offset) % connections_count
            self.curr_connection_config = self.redundant_servers[curr_server_index]

            try:
                self._execute_remote_call()
                store_server_index(curr_server_index)
                return
            except (
                ConnectionError,
                ConnectionRefusedError,
            ):
                continue
            except ServerResponseError as e:
                self._handle_exception_with_exit_code(
                    True,
                    e,
                    ClientExitCode.ServerError.value,
                )

        self._handle_exception_with_exit_code(
            True,
            ConnectionError(f"Unable to connect to any of [{connections_count}] configured connections"),
            ClientExitCode.ConnectionError.value,
        )
