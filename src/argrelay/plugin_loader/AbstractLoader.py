from argrelay.meta_data.StaticData import StaticData
from argrelay.misc_helper.AbstractPlugin import AbstractPlugin


class AbstractLoader(AbstractPlugin):

    def update_static_data(self, static_data: StaticData) -> StaticData:
        pass
