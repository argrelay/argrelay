from argrelay.misc_helper.AbstractPlugin import AbstractPlugin
from argrelay.runtime_data.StaticData import StaticData


class AbstractLoader(AbstractPlugin):

    def update_static_data(
        self,
        static_data: StaticData,
    ) -> StaticData:
        pass
