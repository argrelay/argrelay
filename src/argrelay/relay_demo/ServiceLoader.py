from __future__ import annotations

from argrelay.api_ext.meta_data.DataObjectSchema import (
    object_data_,
    object_id_,
    object_class_,
)
from argrelay.api_ext.meta_data.FunctionObjectDataSchema import accept_object_classes_
from argrelay.api_ext.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.api_ext.relay_server.AbstractLoader import AbstractLoader
from argrelay.api_ext.relay_server.StaticData import StaticData
from argrelay.api_ext.relay_server.StaticDataSchema import types_to_values_
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceObjectClass import ServiceObjectClass


def _todo(self):
    # TODO: this should be generic config for (ServiceArgType, value) -> assignment of implicit args in completion mode.
    #       It is actually, when one of the objects is singled-out.
    #       "default vs implicit":
    #       But setting it as implicit args means situation of searching objects contained by it.
    #       Another situation is continue searching objects outside of it - implicit args should not be used.
    # host_name_to_args: dict[str, dict[ServiceArgType, str]]
    self.host_name_to_args = {
        "qwer": {
            ServiceArgType.CodeMaturity: "dev",
            ServiceArgType.FlowStage: "upstream",
            ServiceArgType.GeoRegion: "amer",
        }
    }

    # TODO: add generic config for (ServiceArgType, value) -> assignment of implicit args in invocation mode.

    # TODO: implement generic logic and config when one of the arg makes other required.
    # TODO: implement generic logic and config when one of the arg proposes values for other.


class ServiceLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:

        static_data = self.load_types_to_values(static_data)
        static_data = self.load_data_objects(static_data)

        return static_data

    def load_types_to_values(self, static_data: StaticData) -> StaticData:
        """
        The loader simply merges content its `config_dict` into `static_data`.
        """

        config_types_to_values: dict[str, list[str]] = self.config_dict[types_to_values_]
        for type_name, values_list in config_types_to_values.items():
            if type_name in static_data.types_to_values:
                static_data.types_to_values[type_name].extend(values_list)
            else:
                static_data.types_to_values[type_name] = values_list

        return static_data

    # noinspection PyMethodMayBeStatic
    def load_data_objects(self, static_data: StaticData) -> StaticData:
        """
        The loader hard-codes samples into `static_data["data_objects"]`
        """

        static_data.data_objects.extend([

            ############################################################################################################
            # functions

            {
                object_id_: "goto",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
            },
            {
                object_id_: "desc",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
            },
            {
                object_id_: "list",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
            },

            ############################################################################################################
            # hosts

            {
                object_id_: "qwer",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
            },
            {
                object_id_: "asdf",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
            },
            {
                object_id_: "zxcv",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
            },

            ############################################################################################################
            # services

            {
                object_id_: "qwer.service_a",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
                ServiceArgType.ServiceName.name: "service_a",
            },
            {
                object_id_: "asdf.service_b",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
                ServiceArgType.ServiceName.name: "service_b",
            },
            {
                object_id_: "zxcv.service_c",
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
                ServiceArgType.ServiceName.name: "service_c",
            },

        ])

        return static_data
