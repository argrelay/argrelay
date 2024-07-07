from argrelay.relay_client.ClientAbstract import ClientAbstract
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.test_infra.ClientCommandFactoryLocal import ClientCommandFactoryLocal


class ClientLocal(ClientAbstract):
    """
    Client local to server

    `ClientLocal` always talks to `LocalServer` via direct func calls (without communication layer).

    Note that all this split for :class:`ClientLocal` and :class:`ClientRemote` (and related other classes) is in
    anticipation that there is a way to keep data persisted in offline/local index which allows
    for the server to be embedded in the client (which can only be practical if server start time is negligible).
    Currently, :class:`ClientLocal` is mostly used for simpler testing (by embedding the `LocalServer`):
    *   Run client and server embedded in the same process.
    *   Avoid communication over the network.
    Access to `LocalServer` in tests:
    *   Func `main()` on client side returns `ClientCommandLocal` in case of `ClientLocal`.
    *   `ClientCommandLocal.local_server` is the `LocalServer` instance to inspection in tests.
    """

    def __init__(
        self,
        client_config: ClientConfig,
    ):
        super().__init__(
            client_config,
            ClientCommandFactoryLocal(),
        )
        assert client_config.use_local_requests
