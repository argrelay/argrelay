from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.relay_server.QueryEngine import QueryEngine


class HelpHintCache:
    """
    Implements FS_94_30_49_28 help hint.
    """

    def __init__(
        self,
        query_engine: QueryEngine,
    ):
        self.query_engine: QueryEngine = query_engine
        self.help_hint_dict: dict = {}

    def populate_cache(self):

        help_hint_envelopes = self.query_engine.query_data_envelopes(
            ReservedEnvelopeClass.class_help.name,
            {
                f"{ReservedPropName.envelope_class.name}": f"{ReservedEnvelopeClass.class_help.name}",
            },
        )

        for help_hint_envelope in help_hint_envelopes:
            prop_name = help_hint_envelope[ReservedPropName.prop_name.name]
            prop_value = help_hint_envelope[ReservedPropName.prop_value.name]
            help_hint = help_hint_envelope[ReservedPropName.help_hint.name]
            if prop_name not in self.help_hint_dict:
                self.help_hint_dict[prop_name] = {}
            self.help_hint_dict[prop_name][prop_value] = help_hint

    def get_value_with_help_hint(
        self,
        prop_name: str,
        prop_value: str,
    ) -> str:
        if prop_name in self.help_hint_dict:
            if prop_value in self.help_hint_dict[prop_name]:
                return f"{prop_value} # {self.help_hint_dict[prop_name][prop_value]}"
        return prop_value
