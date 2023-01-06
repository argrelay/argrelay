from __future__ import annotations

from argrelay.data_schema.DataObjectSchema import (
    object_data_,
    object_id_,
    object_class_,
)
from argrelay.data_schema.FunctionObjectDataSchema import accept_object_classes_
from argrelay.data_schema.StaticDataSchema import types_to_values_
from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.GlobalArgType import GlobalArgType
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

        # TODO: This loader overwrites existing object list (it has to patch it instead).
        #       This is fine for now because `ServiceLoader` is used first in config.
        data_objects = [

            ############################################################################################################
            # functions

            # TODO: As of now, `ServiceLoader` is configured first (after `GitRepoLoader`), so it works.
            #       But to be robust against re-ordering, this loader should shared function names like
            #       "desc", "list", "goto" to accept `GitRepoObjectClass` in addition to `ServiceObjectClass`.
            {
                object_id_: "goto_host",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                object_id_: "goto_service",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "service",
            },
            {
                object_id_: "desc_host",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                object_id_: "desc_service",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "service",
            },
            # TODO: Finalize (and test):
            #       Can there be functions accepting different objects classes
            #       (not like goto_host and goto_service specific for each)?
            #       When "list" `accept_object_classes_` including both host and servie
            #       (ServiceObjectClass.ClassService.name and ServiceObjectClass.ClassHost.name),
            #       will it accept 2 (ALL) via AND or 1 (ANY) via OR?
            #       Is such distinction required?
            {
                object_id_: "list",
                object_class_: ReservedObjectClass.ClassFunction.name,
                object_data_: {
                    accept_object_classes_: [
                        ServiceObjectClass.ClassService.name,
                        ServiceObjectClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "list",
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

            {
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "wert",
            },
            {
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "sdfg",
            },
            {
                object_class_: ServiceObjectClass.ClassHost.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "xcvb",
            },

            ############################################################################################################
            # services

            {
                object_class_: ServiceObjectClass.ClassService.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
                ServiceArgType.ServiceName.name: "service_a",
            },
            {
                object_class_: ServiceObjectClass.ClassService.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
                ServiceArgType.ServiceName.name: "service_b",
            },
            {
                object_class_: ServiceObjectClass.ClassService.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
                ServiceArgType.ServiceName.name: "service_c",
            },

            {
                object_class_: ServiceObjectClass.ClassService.name,
                object_data_: {
                },
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "poiu",
                ServiceArgType.ServiceName.name: "service_c",
            },
        ]

        self.generate_object_id(data_objects)

        static_data.data_objects.extend(data_objects)

        return static_data

    # noinspection PyMethodMayBeStatic
    def generate_object_id(self, data_objects: list):
        for object_data in data_objects:
            if object_id_ not in object_data:
                if object_class_ == ServiceObjectClass.ClassHost.name:
                    object_data[object_id_] = object_data[ServiceArgType.HostName.name]
                if object_class_ == ServiceObjectClass.ClassService.name:
                    object_data[object_id_] = (
                        object_data[ServiceArgType.HostName.name]
                        + "." +
                        object_data[ServiceArgType.ServiceName.name]
                    )
