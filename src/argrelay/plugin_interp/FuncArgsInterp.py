from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InitControl import InitControl
from argrelay.runtime_context.InterpContext import (
    InterpContext,
    function_envelope_ipos_,
)
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FuncArgsInterpConfigSchema import function_search_control_, function_init_control_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
)
from argrelay.schema_config_interp.InitControlSchema import init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc

"""
This module auto-completes command line args when integrated with shell (Bash).

See use case: derived :class:`DemoInterp`.
"""


class FuncArgsInterp(AbstractInterp):

    def __init__(
        self,
        interp_factory_id,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
        )

        # Allocate first container for function `data_envelope`:
        self.base_envelope_ipos += 1
        self.interp_ctx.envelope_containers.append(EnvelopeContainer(SearchControl()))

        self.select_next_container()
        self._apply_function_init_control()
        self._apply_function_search_control()

    def _apply_function_init_control(self):
        # Function `init_control` is based on plugin config (rather than logic):
        self.interp_ctx.curr_container.assigned_types_to_values[
            ReservedArgType.EnvelopeClass.name
        ] = AssignedValue(
            ReservedEnvelopeClass.ClassFunction.name,
            ArgSource.InitValue,
        )
        function_init_control: InitControl = init_control_desc.dict_schema.load(
            self.config_dict[function_init_control_]
        )
        for prop_type, prop_value in function_init_control.init_types_to_values.items():
            self.interp_ctx.curr_container.assigned_types_to_values[prop_type] = AssignedValue(
                prop_value,
                ArgSource.InitValue,
            )
            if prop_type in self.interp_ctx.curr_container.remaining_types_to_values:
                del self.interp_ctx.curr_container.remaining_types_to_values[prop_type]

    def _apply_function_search_control(self, ):
        # Function `search_control` is based on plugin config (rather than data found in `data_envelope`):
        self.interp_ctx.curr_container.search_control = search_control_desc.dict_schema.load(
            self.config_dict[function_search_control_]
        )

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        """
        Scans through `unconsumed_tokens` and tries to match its value against values of each type.
        """

        consumed_token_ipos_list = []
        for unconsumed_token_ipos in self.interp_ctx.unconsumed_tokens:
            unconsumed_token = self.interp_ctx.parsed_ctx.all_tokens[unconsumed_token_ipos]
            # See if token matches any type by value:

            for arg_type, arg_values in self.interp_ctx.curr_container.remaining_types_to_values.items():
                if unconsumed_token in arg_values:
                    self.interp_ctx.curr_container.assigned_types_to_values[arg_type] = AssignedValue(
                        unconsumed_token,
                        ArgSource.ExplicitPosArg,
                    )
                    consumed_token_ipos_list.append(unconsumed_token_ipos)
                    self.interp_ctx.consumed_tokens.append(unconsumed_token_ipos)
                    # TD_76_09_29_31: overlapped
                    # Assign matching unconsumed arg value to the first type it matches (only once):
                    del self.interp_ctx.curr_container.remaining_types_to_values[arg_type]
                    break

        # perform list modifications out of the prev loop:
        for consumed_token_ipos in consumed_token_ipos_list:
            self.interp_ctx.unconsumed_tokens.remove(consumed_token_ipos)

    def try_iterate(self) -> InterpStep:
        """
        Try to consume more args if possible.

        *   If function was found, start with search for its first envelope class.
        *   If curr envelope class is found, move to the next (until all are found).

        :returns:
        *   `InterpStep.NextInterp`: move to next interpreter: curr interpreter is fully satisfied from the args
        *   `InterpStep.NextEnvelope`: call again curr interpreter: still more things to find in the args
        *   `InterpStep.StopAll`: interpreter sees no point to continue the loop (`InterpContext.interpret_command`)
        """

        # We want single `data_envelope` to be found, not zero, not more than one:
        if self.interp_ctx.curr_container.found_count > 1:
            # Too many `data_envelope`-s - stop:
            return InterpStep.StopAll
        elif self.interp_ctx.curr_container.found_count == 1:

            if self.interp_ctx.curr_container_ipos == self.base_envelope_ipos:
                # This is a function envelope:
                search_control_list: list[SearchControl] = self.get_search_control_list()
                # Create `EnvelopeContainer`-s for every envelope to find:
                self.interp_ctx.alloc_searchable_containers(search_control_list)

            if self.interp_ctx.is_last_container():
                # Function does not need any envelopes:
                return InterpStep.NextInterp
            else:
                self.select_next_container()
                self.run_init_control()
                # Need more args to consume for the next envelope to find:
                return InterpStep.NextEnvelope

        else:
            # No `data_envelope` = nothing to do:
            return InterpStep.StopAll

    def get_search_control_list(self) -> list[SearchControl]:
        delegator_plugin = self.get_funct_delegator()
        search_control_list: list[SearchControl] = delegator_plugin.run_search_control(self.get_funct_data_envelope())
        return search_control_list

    def run_init_control(self):
        delegator_plugin = self.get_funct_delegator()
        delegator_plugin.run_init_control(
            self.interp_ctx.envelope_containers,
            self.interp_ctx.curr_container_ipos,
        )

    def run_fill_control(self):
        self.get_funct_delegator().run_fill_control(
            self.interp_ctx,
        )

    def get_funct_data_envelope(self):
        return self.interp_ctx.envelope_containers[self.base_envelope_ipos + function_envelope_ipos_].data_envelope

    def get_funct_delegator(self):
        delegator_plugin_instance_id = self.get_funct_data_envelope()[instance_data_][delegator_plugin_instance_id_]
        delegator_plugin: AbstractDelegator = self.interp_ctx.action_delegators[delegator_plugin_instance_id]
        return delegator_plugin

    def select_next_container(self):
        self.interp_ctx.curr_container_ipos += 1
        self.interp_ctx.curr_container = self.interp_ctx.envelope_containers[
            self.interp_ctx.curr_container_ipos
        ]

    def next_interp(self) -> "AbstractInterp":
        delegator_plugin = self.get_funct_delegator()
        interp_factory_id = delegator_plugin.run_interp_control(self)
        if interp_factory_id:
            return self.interp_ctx.create_next_interp(interp_factory_id)
        else:
            return None

    def propose_arg_completion(self) -> None:
        self.interp_ctx.comp_suggestions.extend(self.propose_auto_comp_list())

    def propose_auto_comp_list(self) -> list[str]:

        # TODO: POC: Either remove it or implement properly: just testing named args:
        if (
            self.interp_ctx.parsed_ctx.tan_token_l_part.endswith(":")
            or
            self.interp_ctx.parsed_ctx.tan_token_r_part.startswith(":")
        ):
            return [
                type_name + SpecialChar.KeyValueDelimiter.value
                for type_name in self.interp_ctx.curr_container.search_control.types_to_keys_dict.keys()
                if not type_name.startswith("_")
            ]

        if self.interp_ctx.parsed_ctx.comp_type == CompType.SubsequentHelp:
            if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
                return self.remaining_from_next_missing_type()
            else:
                # TODO: Suggest keys (:) of missing types instead - it is `SubsequentHelp`, user insist and wants something else:
                return self.remaining_from_next_missing_type()

        if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
            if (
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixHidden or
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixShown or
                self.interp_ctx.parsed_ctx.comp_type == CompType.MenuCompletion
            ):
                # Cannot complete => show first missing:
                first_missing_type_values = self.remaining_from_next_missing_type()
                if first_missing_type_values:
                    return first_missing_type_values
                else:
                    return []
        else:
            if self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixHidden:
                return self.remaining_from_next_missing_type()
            if self.interp_ctx.parsed_ctx.comp_type == CompType.MenuCompletion:
                # Note that this space will be cached by shell and used without completion script invocation
                # until cycling through these options by repetitive menu completion is not over.
                # TODO: Test cycling through options limited by current prefix (versus cycling through every item at current arg space):
                return self.remaining_from_next_missing_type()
            if self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixShown:
                # Can complete => show matching:
                return self.remaining_from_next_missing_type()
            else:
                return self.remaining_from_next_missing_type()

    def remaining_from_next_missing_type(self) -> list[str]:
        """
        Clarifications:
        *   remaining = because values for the given type are reduced based on narrowed down `data_envelope` set
        *   missing = because this arg type is not specified yet
        *   next = because arg types are tired in specific order
        """
        proposed_values: list[str] = []

        # Return filtered value set from the next missing arg:
        for arg_type in self.interp_ctx.curr_container.search_control.types_to_keys_dict.keys():
            if (
                # TODO: only one condition should be enough: arg_type is either in one or in another, not in both:
                arg_type not in self.interp_ctx.curr_container.assigned_types_to_values
                and
                arg_type in self.interp_ctx.curr_container.remaining_types_to_values
            ):
                proposed_values = [
                    # FS_71_87_33_52: `help_hint`:
                    self.interp_ctx.help_hint_cache.get_value_with_help_hint(arg_type, x)
                    for x in self.interp_ctx.curr_container.remaining_types_to_values[arg_type]
                    if (
                        isinstance(x, str)
                        and
                        # FS_32_05_46_00: using `startwith`:
                        x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                        # TODO: Support list[str] - what if one type can have list of values (and we need to match any as in OR)?
                    )
                ]
                if proposed_values:
                    # Collect only until the first proposed value set from missing args:
                    break

        return proposed_values
