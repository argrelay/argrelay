from argrelay_app_client.relay_client.ClientAbstract import ClientAbstract
from argrelay_app_client.relay_client.ClientCommandFactoryRemote import (
    ClientCommandFactoryRemote,
)
from argrelay_lib_root.enum_desc.ProcRole import ProcRole
from argrelay_schema_config_client.runtime_data_client_app.ClientConfig import (
    ClientConfig,
)


class ClientRemote(ClientAbstract):
    """
    Client remote to server

    It talks to `CustomFlaskApp` which is remote server in this case.

    See also `ClientLocal` and `LocalServer`.
    """

    def __init__(
        self,
        client_config: ClientConfig,
        proc_role: ProcRole,
        w_pipe_end,
        is_optimized_completion: bool,
        server_index: int,
    ):
        super().__init__(
            client_config,
            ClientCommandFactoryRemote(
                client_config,
                proc_role,
                w_pipe_end,
                is_optimized_completion,
                server_index,
            ),
        )
        assert not client_config.use_local_requests
