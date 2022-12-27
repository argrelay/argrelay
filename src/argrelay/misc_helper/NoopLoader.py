from argrelay.api_ext.relay_server.AbstractLoader import AbstractLoader
from argrelay.api_ext.relay_server.StaticData import StaticData


class NoopLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:
        return static_data
