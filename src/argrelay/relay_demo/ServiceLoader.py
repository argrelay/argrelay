from __future__ import annotations

from argrelay.data_schema.DataObjectSchema import (
    object_data_,
    object_id_,
    object_class_,
)
from argrelay.data_schema.FunctionObjectDataSchema import accept_object_classes_
from argrelay.data_schema.StaticDataSchema import types_to_values_
from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.meta_data.StaticData import StaticData
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceObjectClass import ServiceObjectClass


def _todo(self):
    # TODO: this should be generic config for (ServiceArgType, value) -> assignment of implicit args in completion mode.
    #       It is actually, when one of the objects is singled-out.
    #       "default vs implicit":
    #       But setting it as implicit args means situation of searching objects contained by it.
    #       Another situation is to continue searching objects outside of it - implicit args should not be used.
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

        object_list = [

            ############################################################################################################
            # functions

            {
                object_id_: "goto_host",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
                ServiceArgType.ActionType.name: "goto",
                ServiceArgType.ObjectSelector.name: "host",
            },
            {
                object_id_: "goto_service",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                    ],
                },
                ServiceArgType.ActionType.name: "goto",
                ServiceArgType.ObjectSelector.name: "service",
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
                ServiceArgType.ActionType.name: "desc",
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
                ServiceArgType.ActionType.name: "list",
            },

            ############################################################################################################
            # hosts

            {
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
            },
            {
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
            },
            {
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
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
                ServiceArgType.ServiceName.name: "service_c",
            },
        ]

        self.generate_object_id(object_list)

        static_data.data_objects.extend(object_list)

        return static_data

    # noinspection PyMethodMayBeStatic
    def generate_object_id(self, object_list: list):
        for object_data in object_list:
            if object_id_ not in object_data:
                if object_class_ == ServiceObjectClass.ClassHost.name:
                    object_data[object_id_] = object_data[ServiceArgType.HostName.name]
                if object_class_ == ServiceObjectClass.ClassService.name:
                    object_data[object_id_] = (
                        object_data[ServiceArgType.HostName.name]
                        + "." +
                        object_data[ServiceArgType.ServiceName.name]
                    )
