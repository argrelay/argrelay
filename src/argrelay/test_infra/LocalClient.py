from argrelay.relay_client.AbstractClient import AbstractClient
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.test_infra.LocalClientCommandFactory import LocalClientCommandFactory


class LocalClient(AbstractClient):
    """
    Client local to server

    `LocalClient` always talks to `LocalServer` via direct func calls (without communication layer).

    Note that all this split for :class:`LocalClient` and :class:`RemoteClient` (and related other classes) is in
    anticipation that there is a way to keep data persisted in offline/local index which allows
    for the server to be embedded in the client (which can only be practical if server start time is negligible).
    Currently, :class:`LocalClient` is mostly used for simpler testing (by embedding the `LocalServer`):
    *   Run client and server embedded in the same process.
    *   Avoid communication over the network.
    Access to `LocalServer` in tests:
    *   Func `main()` on client side returns `AbstractLocalClientCommand` in case of `LocalClient`.
    *   `AbstractLocalClientCommand.local_server` is the `LocalServer` instance to inspection in tests.
    """

    def __init__(self, client_config: ClientConfig):
        super().__init__(
            client_config,
            LocalClientCommandFactory(),
        )
        assert client_config.use_local_requests
