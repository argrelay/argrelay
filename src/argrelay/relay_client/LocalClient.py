from argrelay.relay_client.AbstractClient import AbstractClient
from argrelay.relay_client.LocalClientCommandFactory import LocalClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig


class LocalClient(AbstractClient):
    """
    Client local to server

    Note that all this split for :class:`LocalClient` and :class:`RemoteClient` (and related extra classes) is in
    anticipation that there is a way to keep data persisted in offline/local index which allows
    for the server to be embedded in the client (which can only be practical if server start time is negligible).
    Currently, :class:`LocalClient` is mostly used for simpler testing (by embedding the server).
    """

    def __init__(self, client_config: ClientConfig):
        super().__init__(
            client_config,
            LocalClientCommandFactory(),
        )
        assert client_config.use_local_requests
