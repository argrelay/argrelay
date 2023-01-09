from argrelay.meta_data.StaticData import StaticData
from argrelay.plugin_loader.AbstractLoader import AbstractLoader


class NoopLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:
        return static_data
