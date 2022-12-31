from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.StaticData import StaticData


class NoopLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:
        return static_data
