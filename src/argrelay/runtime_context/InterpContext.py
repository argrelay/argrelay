from __future__ import annotations

from dataclasses import field, dataclass

from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.RunMode import RunMode
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_class_, context_control_
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc


@dataclass
class InterpContext:
    """
    Mutable state for the process of command line interpretation.
    """

    parsed_ctx: ParsedContext

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that).
    interp_factories: dict[str, "AbstractInterpFactory"]
    """
    Reference to `ServerConfig.action_invocators`.
    """

    action_invocators: dict[str, "AbstractInvocator"]
    """
    Reference to `ServerConfig.action_invocators`.
    """

    mongo_db: Database

    mongo_col: Collection = field(init = False)

    unconsumed_tokens: list[int] = field(init = False)
    """
    Remaining tokens (their ipos) which are still unconsumed (in ascending order).
    """

    consumed_tokens: list[int] = field(init = False, default_factory = lambda: [])
    """
    Already consumed tokens (their ipos) in the order of their consumption.
    """

    envelope_containers: list[EnvelopeContainer] = field(init = False, default_factory = lambda: [])
    """
    Associated data for each `data_envelope` to be found.
    """

    curr_container: EnvelopeContainer = field(init = False, default_factory = lambda: EnvelopeContainer())
    """
    The `envelope_containers` currently being searched.
    """

    # When `function_envelope` found, it is an ipos into `search_control_list` to select curr `search_control`:
    curr_container_ipos: int = field(init = False, default = -1)

    last_found_envelope_ipos: int = field(init = False, default = -1)
    """
    An ipos into `envelope_containers` for the last found envelope.
    Because of multiple or zero candidates (not singled out), the tail of `envelope_containers` starting after
    `last_found_envelope_ipos` is not pointing to `data_envelope`-s found.
    """

    prev_interp: "AbstractInterp" = field(init = False, default = None)

    curr_interp: "AbstractInterp" = field(init = False, default = None)
    """
    Current interpreter during command line interpretation.
    """

    comp_suggestions: list = field(init = False, default_factory = lambda: [])

    def __post_init__(self):
        self.unconsumed_tokens = self._init_unconsumed_tokens()
        self.mongo_col = self.mongo_db[data_envelopes_]
        self.envelope_containers.append(self.curr_container)

    def _init_unconsumed_tokens(self):
        return [
            token_ipos for token_ipos in range(0, len(self.parsed_ctx.all_tokens))
            if (
                (
                    self.parsed_ctx.run_mode == RunMode.CompletionMode
                    and
                    # Completion mode excludes tangent token because it is supposed to be completed:
                    token_ipos != self.parsed_ctx.tan_token_ipos
                )
                or
                (
                    self.parsed_ctx.run_mode == RunMode.InvocationMode
                )
            )
        ]

    def create_containers(self, search_control_list):
        for search_control in search_control_list:
            envelope_container = EnvelopeContainer(
                search_control_desc.dict_schema.load(
                    search_control
                )
            )
            self.envelope_containers.append(envelope_container)

    def is_last_container(self) -> bool:
        return self.curr_container_ipos + 1 == len(self.envelope_containers)

    def init_next_container(self):
        self.curr_container_ipos += 1
        self.curr_container = self.envelope_containers[
            self.curr_container_ipos
        ]
        self._propagate_implicit_values()

    def _propagate_implicit_values(self):
        """
        FS_46_96_59_05:
        Copy arg value from prev `data_envelope` for arg types specified in `context_control` into next `arg_context`.
        """
        if self.last_found_envelope_ipos >= 0:
            prev_envelope = self.envelope_containers[
                self.last_found_envelope_ipos
            ]
            if context_control_ in prev_envelope.data_envelope:
                arg_type_list_to_push = prev_envelope.data_envelope[context_control_]
                for arg_type_to_push in arg_type_list_to_push:
                    if arg_type_to_push in prev_envelope.data_envelope:
                        if arg_type_to_push in self.curr_container.assigned_types_to_values:
                            arg_value = self.curr_container.assigned_types_to_values[
                                arg_type_to_push
                            ]
                            if arg_value.arg_source.value <= ArgSource.ImplicitValue.value:
                                # Override value with source of higher priority:
                                arg_value.arg_source = ArgSource.ImplicitValue
                                arg_value.arg_value = prev_envelope.data_envelope[arg_type_to_push]
                        else:
                            self.curr_container.assigned_types_to_values[
                                arg_type_to_push
                            ] = AssignedValue(
                                prev_envelope.data_envelope[arg_type_to_push],
                                ArgSource.ImplicitValue,
                            )

    def query_envelopes(self):
        ElapsedTime.measure(f"begin_query_envelopes: {self.curr_container.search_control.envelope_class}")
        query_dict = {
            envelope_class_: self.curr_container.search_control.envelope_class,
        }
        # FS_31_70_49_15: populate arg values to search from the context:
        for arg_type in self.curr_container.search_control.types_to_keys_dict.keys():
            if arg_type in self.curr_container.assigned_types_to_values:
                query_dict[arg_type] = self.curr_container.assigned_types_to_values[arg_type].arg_value

        # TODO: How to query values contained in arrays? For example, `GitRepoRelPath` is array. How to query envelopes which contain given value in elements of the array?
        ElapsedTime.measure("before_mongo_find")
        query_res = self.mongo_col.find(query_dict)
        ElapsedTime.measure("after_mongo_find")
        self.curr_container.update_curr_remaining_types_to_values(query_res)
        ElapsedTime.measure(f"end_query_envelopes: {query_dict.keys()} {self.curr_container.found_count}")

    def register_found_envelope(self):
        self.last_found_envelope_ipos += 1
        self.curr_container.populate_implicit_arg_values()

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that) together with this loop:
    def interpret_command(self, first_interp_factory_id: str) -> None:
        """
        Main interpretation loop.

        Start with initial interpreter and continue until curr interpreter returns no more next interpreter.
        """

        interp_n: int = 0
        self.curr_interp = self.create_next_interp(first_interp_factory_id)
        while self.curr_interp:
            interp_n += 1
            ElapsedTime.measure(f"[i={interp_n}]: before_consume_args: {type(self.curr_interp).__name__}")

            self.curr_interp.consume_key_args()
            self.curr_interp.consume_pos_args()

            ElapsedTime.measure(f"[i={interp_n}]: before_try_iterate: {type(self.curr_interp).__name__}")
            interp_step: InterpStep = self.curr_interp.try_iterate()
            if interp_step == InterpStep.NextEnvelope:
                continue
            elif interp_step == InterpStep.StopAll:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                return
            elif interp_step == InterpStep.NextInterp:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self.prev_interp = self.curr_interp
                self.curr_interp = self.curr_interp.next_interp()
                pass
            else:
                raise RuntimeError(interp_step)

    def _contribute_to_completion(self):
        if self.parsed_ctx.run_mode == RunMode.CompletionMode:
            # Each in the chains of interpreters hava a chance to suggest completion values (contribute):
            self.curr_interp.propose_arg_completion()

    def propose_arg_values(self) -> list[str]:
        return self.comp_suggestions

    def create_next_interp(self, interp_factory_id: str) -> "AbstractInterp":
        interp_factory: "AbstractInterpFactory" = self.interp_factories[interp_factory_id]
        return interp_factory.create_interp(self)

    def get_data_envelopes(self):
        return [envelope_container.data_envelope for envelope_container in self.envelope_containers]

    def print_debug(self, end_str: str = "\n") -> None:
        if not self.parsed_ctx.is_debug_enabled:
            return
        self.parsed_ctx.print_debug("")
        eprint(TermColor.DEBUG.value, end = "")
        eprint(f"comp_suggestions: {self.comp_suggestions}", end = " ")
        eprint(TermColor.RESET.value, end = end_str)
