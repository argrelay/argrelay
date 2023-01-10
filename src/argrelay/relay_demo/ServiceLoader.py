from __future__ import annotations

from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.meta_data.StaticData import StaticData
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.schema_config_core_server.StaticDataSchema import types_to_values_
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
    envelope_class_,
)
from argrelay.schema_config_interp.FunctionEnvelopePayloadSchema import accept_envelope_classes_, invocator_plugin_id_


def _todo(self):
    # TODO: this should be generic config for (ServiceArgType, value) -> assignment of implicit args in completion mode.
    #       It is actually, when one of the envelope is singled-out.
    #       "default vs implicit":
    #       But setting it as implicit args means situation of searching objects contained by it.
    #       Another situation is to continue searching envelopes outside of it - implicit args should not be used.
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
        static_data = self.load_data_envelopes(static_data)

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
    def load_data_envelopes(self, static_data: StaticData) -> StaticData:
        """
        The loader hard-codes samples into `static_data["data_envelopes"]`
        """

        # TODO: This loader overwrites existing object list (it has to patch it instead).
        #       This is fine for now because `ServiceLoader` is used first in config.
        data_envelopes = [

            ############################################################################################################
            # functions

            # TODO: As of now, `ServiceLoader` is configured first (after `GitRepoLoader`), so it works.
            #       But to be robust against re-ordering, this loader should shared function names like
            #       "desc", "list", "goto" to accept `GitRepoEnvelopeClass` in addition to `ServiceEnvelopeClass`.
            {
                envelope_id_: "goto_host",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                envelope_payload_: {
                    invocator_plugin_id_: ErrorInvocator.__name__,
                    accept_envelope_classes_: [
                        ServiceEnvelopeClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: "goto_service",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                envelope_payload_: {
                    invocator_plugin_id_: ErrorInvocator.__name__,
                    accept_envelope_classes_: [
                        ServiceEnvelopeClass.ClassService.name,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "service",
            },
            {
                envelope_id_: "desc_host",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                envelope_payload_: {
                    accept_envelope_classes_: [
                        ServiceEnvelopeClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: "desc_service",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                envelope_payload_: {
                    accept_envelope_classes_: [
                        ServiceEnvelopeClass.ClassService.name,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "service",
            },
            # TODO: Finalize (and test):
            #       Can there be functions accepting different envelopes classes
            #       (not like goto_host and goto_service specific for each)?
            #       When "list" `accept_envelope_classes_` including both host and servie
            #       (ServiceEnvelopeClass.ClassService.name and ServiceEnvelopeClass.ClassHost.name),
            #       will it accept 2 (ALL) via AND or 1 (ANY) via OR?
            #       Is such distinction required?
            {
                envelope_id_: "list",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                envelope_payload_: {
                    accept_envelope_classes_: [
                        ServiceEnvelopeClass.ClassService.name,
                        ServiceEnvelopeClass.ClassHost.name,
                    ],
                },
                GlobalArgType.ActionType.name: "list",
            },

            ############################################################################################################
            # hosts

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "wert",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "sdfg",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "xcvb",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                    "test_data": "TD-2023-01-07--1"
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "amer.us",
                ServiceArgType.HostName.name: "amer.us",
            },

            ############################################################################################################
            # services

            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.HostName.name: "qwer",
                ServiceArgType.ServiceName.name: "service_a",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.HostName.name: "asdf",
                ServiceArgType.ServiceName.name: "service_b",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "zxcv",
                ServiceArgType.ServiceName.name: "service_c",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.HostName.name: "poiu",
                ServiceArgType.ServiceName.name: "service_c",
            },
        ]

        self.generate_envelope_id(data_envelopes)

        static_data.data_envelopes.extend(data_envelopes)

        return static_data

    # noinspection PyMethodMayBeStatic
    def generate_envelope_id(self, data_envelopes: list):
        for data_envelope in data_envelopes:
            if envelope_id_ not in data_envelope:
                if envelope_class_ == ServiceEnvelopeClass.ClassHost.name:
                    data_envelope[envelope_id_] = data_envelope[ServiceArgType.HostName.name]
                if envelope_class_ == ServiceEnvelopeClass.ClassService.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServiceArgType.HostName.name]
                        + "." +
                        data_envelope[ServiceArgType.ServiceName.name]
                    )
