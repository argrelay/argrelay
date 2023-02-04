from argrelay.relay_client.AbstractClient import AbstractClient
from argrelay.relay_client.RemoteClientCommandFactory import RemoteClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig


class RemoteClient(AbstractClient):
    """
    Client remote to server

    It talks to `CustomFlaskApp` which is remote server in this case.

    See also `LocalClient` and `LocalServer`.
    """

    def __init__(self, client_config: ClientConfig):
        super().__init__(
            client_config,
            RemoteClientCommandFactory(client_config),
        )
        assert not client_config.use_local_requests
