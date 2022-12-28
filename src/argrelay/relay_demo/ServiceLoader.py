from __future__ import annotations

from argrelay.api_ext.relay_server.AbstractLoader import AbstractLoader
from argrelay.api_ext.relay_server.StaticData import StaticData
from argrelay.relay_demo.ServiceArgType import ServiceArgType


def _todo(self):
    # TODO: this should be generic config for (ServiceArgType, value) -> assignment of implicit args in completion mode.
    #       It is actually, when one of the objects is singled-out.
    #       "default vs implicit":
    #       But setting it as implicit args means situation of searching objects contained by it.
    #       Another situation is continue searching objects outside of it - implicit args should not be used.
    # host_name_to_args: dict[str, dict[ServiceArgType, str]]
    self.host_name_to_args = {
        "qwer": {
            ServiceArgType.CodeMaturity: "uat",
            ServiceArgType.FlowStage: "upstream",
            ServiceArgType.GeoRegion: "amer",
        }
    }

    # TODO: add generic config for (ServiceArgType, value) -> assignment of implicit args in invocation mode.

    # TODO: implement generic logic and config when one of the arg makes other required.
    # TODO: implement generic logic and config when one of the arg proposes values for other.


class ServiceLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:
        """
        The loader simply merges content its `config_dict` into `static_data`.
        """

        loaded_data: dict[str, dict[str, list[str]]] = self.config_dict["types_to_values"]
        for type_name, values_list in loaded_data.items():
            if type_name in static_data.types_to_values:
                static_data.types_to_values[type_name] + values_list
            else:
                static_data.types_to_values[type_name] = values_list
        return static_data
