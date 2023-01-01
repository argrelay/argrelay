from __future__ import annotations

from dataclasses import field, dataclass

from pymongo.database import Database

from argrelay.meta_data import StaticData
from argrelay.meta_data.ArgValue import ArgValue
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.meta_data.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.mongo_data.MongoClientWrapper import get_mongo_client, find_objects
from argrelay.runtime_context.ParsedContext import ParsedContext


@dataclass
class CommandContext:
    """
    Mutable state for the process of command line interpretation.
    """

    parsed_ctx: ParsedContext

    static_data: StaticData

    interp_factories: dict[str, "AbstractInterpFactory"]

    mongo_db: Database

    unconsumed_tokens: list[int] = field(init = False)
    """
    Remaining tokens (their ipos) which are still unconsumed (in ascending order).
    """

    consumed_tokens: list[int] = field(init = False, default_factory = lambda: [])
    """
    Already consumed tokens (their ipos) in the order of their consumption.
    """

    assigned_types_to_values: dict[str, ArgValue] = field(init = False, default_factory = lambda: {})
    """
    All assigned args (from interpreted tokens) mapped as type:value.
    """

    curr_interp: "AbstractInterp" = field(init = False, default = None)
    """
    Current interpreter during command line interpretation.
    """

    comp_suggestions: list = field(init = False, default = lambda: [])

    def __post_init__(self):
        self.unconsumed_tokens = self._init_unconsumed_tokens()

    def _init_unconsumed_tokens(self):
        return [
            ipos for ipos in range(0, len(self.parsed_ctx.all_tokens))
            if (
                (
                    self.parsed_ctx.run_mode == RunMode.CompletionMode
                    and
                    # Completion mode excludes selected token because it is supposed to be completed:
                    ipos != self.parsed_ctx.sel_token_ipos
                )
                or
                (
                    self.parsed_ctx.run_mode == RunMode.InvocationMode
                )
            )
        ]

    def interpret_command(self) -> None:
        self.curr_interp = self.create_next_interp(self.static_data.first_interp_factory_id)
        while self.curr_interp:
            self.curr_interp.consume_key_args()
            self.curr_interp.consume_pos_args()
            if self.parsed_ctx.run_mode == RunMode.CompletionMode:
                self.curr_interp.propose_arg_completion()
            self.curr_interp = self.curr_interp.next_interp()

    # TODO: remove this: the result is returned from server to client for client to execute either print_help or print arg values
    def invoke_action(self) -> None:
        self.print_debug()

        if self.parsed_ctx.comp_type == CompType.DescribeArgs:
            # TODO: send data to client to print this help:
            self.print_help()
            return

        if self.parsed_ctx.run_mode == RunMode.CompletionMode:
            auto_comp: str = self.propose_auto_comp()
            # TODO: send data to client to print parguments:
            print(auto_comp, flush = True)
            return

        if self.parsed_ctx.run_mode == RunMode.InvocationMode:
            # TODO: send data to client to invoke command:
            eprint("no relay implemented yet")
            # TODO: clean up: temporarily implemented to list all objects matching criteria:
            for data_object in find_objects(self.mongo_db, self.assigned_types_to_values):
                print(data_object)

    # TODO: clean up: single line was only useful for local requests:
    def propose_auto_comp(self) -> str:
        if self.comp_suggestions is None:
            raise ValueError("Return value must be list")
        return "\n".join(self.comp_suggestions)

    def propose_arg_values(self) -> list[str]:
        return self.comp_suggestions

    def create_next_interp(self, interp_factory_id: str) -> "AbstractInterp":
        interp_factory: "AbstractInterpFactory" = self.interp_factories[interp_factory_id]
        return interp_factory.create_interp(self)

    def print_help(self) -> None:
        eprint()
        # TODO: print:
        #       * currently selected args in one line: key1:value2 key2:value2
        #       * not selected args spaces in multiple lines: space: value1 value2 ...
        # TODO: print values matching any of the arg types which have already been assigned
        # TODO: print conflicting values (two different implicit values)
        # TODO: print unrecognized tokens
        # TODO: for unrecognized token highlight by color all tokens with matching substring
        is_first_missing_found: bool = False
        for arg_type in self.static_data.types_to_values.keys():
            if not self.is_type_with_values(arg_type):
                continue
            if arg_type in self.assigned_types_to_values:
                eprint(TermColor.DARK_GREEN.value, end = "")
                eprint(f"{arg_type}:", end = "")
                eprint(
                    f" {self.assigned_types_to_values[arg_type].arg_value} " +
                    f"[{self.assigned_types_to_values[arg_type].arg_source}]",
                    end = ""
                )
                eprint(TermColor.RESET.value, end = "")
            else:
                eprint(TermColor.BRIGHT_YELLOW.value, end = "")
                if not is_first_missing_found:
                    eprint(f"*{arg_type}:", end = "")
                    is_first_missing_found = True
                else:
                    eprint(f"{arg_type}:", end = "")
                eprint(f" ?", end = "")
                eprint(TermColor.RESET.value, end = "")
                eprint(
                    f" {'|'.join(self.static_data.types_to_values[arg_type])}",
                    end = ""
                )
            eprint()

    def is_type_with_values(self, arg_type: str) -> bool:
        return len(self.static_data.types_to_values[arg_type]) != 0

    def print_debug(self) -> None:
        if not self.parsed_ctx.is_debug_enabled:
            return
        eprint(TermColor.DEBUG.value)
        eprint(f"\"{self.parsed_ctx.command_line}\"", end = " ")
        eprint(f"cursor_cpos: {self.parsed_ctx.cursor_cpos}", end = " ")
        eprint(f"sel_token_l_part: \"{self.parsed_ctx.sel_token_l_part}\"", end = " ")
        eprint(f"sel_token_r_part: \"{self.parsed_ctx.sel_token_r_part}\"", end = " ")
        eprint(f"comp_type: {self.parsed_ctx.comp_type}", end = " ")
        eprint(f"comp_key: {self.parsed_ctx.comp_key}", end = " ")
        eprint(f"comp_suggestions: {self.comp_suggestions}", end = " ")
        eprint(TermColor.RESET.value)

    def list_objects(self):
        mongo_client = get_mongo_client()
