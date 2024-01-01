from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
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
            ReservedEnvelopeClass.ClassHelp.name,
            {
                f"{ReservedArgType.EnvelopeClass.name}": f"{ReservedEnvelopeClass.ClassHelp.name}",
            },
        )

        for help_hint_envelope in help_hint_envelopes:
            arg_type = help_hint_envelope[ReservedArgType.ArgType.name]
            arg_value = help_hint_envelope[ReservedArgType.ArgValue.name]
            help_hint = help_hint_envelope[ReservedArgType.HelpHint.name]
            if arg_type not in self.help_hint_dict:
                self.help_hint_dict[arg_type] = {}
            self.help_hint_dict[arg_type][arg_value] = help_hint

    def get_value_with_help_hint(
        self,
        arg_type: str,
        arg_value: str,
    ) -> str:
        if arg_type in self.help_hint_dict:
            if arg_value in self.help_hint_dict[arg_type]:
                return f"{arg_value} # {self.help_hint_dict[arg_type][arg_value]}"
        return arg_value
