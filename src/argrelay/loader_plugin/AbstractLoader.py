from argrelay.meta_data.StaticData import StaticData


class AbstractLoader:
    config_dict: dict

    def __init__(self, config_dict: dict):
        self.config_dict = config_dict

    def update_static_data(self, static_data: StaticData) -> StaticData:
        pass
