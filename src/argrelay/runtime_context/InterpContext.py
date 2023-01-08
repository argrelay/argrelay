from __future__ import annotations

from dataclasses import field, dataclass

from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.data_schema.DataObjectSchema import object_class_
from argrelay.data_schema.ObjectClassQuerySchema import keys_to_types_list_
from argrelay.data_schema.StaticDataSchema import data_objects_
from argrelay.meta_data import StaticData
from argrelay.meta_data.ArgValue import ArgValue
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.meta_data.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.mongo_data.MongoClientWrapper import get_mongo_client, find_objects
from argrelay.runtime_context.ParsedContext import ParsedContext

assigned_types_to_values_ = "assigned_types_to_values"
remaining_types_to_values_ = "remaining_types_to_values"

@dataclass
class InterpContext:
    """
    Mutable state for the process of command line interpretation.
    """

    parsed_ctx: ParsedContext

    static_data: StaticData

    interp_factories: dict[str, "AbstractInterpFactory"]

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

    curr_assigned_types_to_values: dict[str, ArgValue] = field(init = False)
    """
    All assigned args (from interpreted tokens) mapped as type:value which belong to `curr_data_object`.
    """

    curr_remaining_types_to_values: dict[str, list[str]] = field(init = False)
    """
    All arg values per type left for suggestion given the `curr_assigned_types_to_values`.
    """

    assigned_types_to_values_per_object: list[dict] = field(init = False, default_factory = lambda: [])
    """
    List of completed results previously accumulated in `curr_assigned_types_to_values`.
    Each element of the list contains a dict with these fields:
    # TODO: Formalize this in schema - see also `GenericInterp.curr_data_object`:
    *   `object_class_`
    *   `object_data_`
    *   `assigned_types_to_values_`
    *   `remaining_types_to_value_`
    *   TODO: maybe also `keys_to_types` (the query)?
    """

    prev_interp: "AbstractInterp" = field(init = False, default = None)

    curr_interp: "AbstractInterp" = field(init = False, default = None)
    """
    Current interpreter during command line interpretation.
    """

    comp_suggestions: list = field(init = False, default_factory = lambda: [])

    def __post_init__(self):
        self.unconsumed_tokens = self._init_unconsumed_tokens()
        self.mongo_col = self.mongo_db[data_objects_]

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
        """
        Main interpretation loop.

        Start with initial interpreter and continue until curr interpreter returns no more next interpreter.
        """
        self.curr_interp = self.create_next_interp(self.static_data.first_interp_factory_id)
        while self.curr_interp:

            self.curr_interp.consume_key_args()
            self.curr_interp.consume_pos_args()

            iter_status: int = self.curr_interp.try_iterate()
            if iter_status > 0:
                continue
            elif iter_status < 0:
                self._contribute_to_completion()
                return

            self._contribute_to_completion()
            self.prev_interp = self.curr_interp
            self.curr_interp = self.curr_interp.next_interp()

    def _contribute_to_completion(self):
        if self.parsed_ctx.run_mode == RunMode.CompletionMode:
            # Each in the chains of interpreters hava a chance to suggest completion values (contribute):
            self.curr_interp.propose_arg_completion()

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
            for data_object in find_objects(self.mongo_db, self.curr_assigned_types_to_values):
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
        for object_result in self.assigned_types_to_values_per_object:
            if object_class_ not in object_result:
                # It must be last object created but no object class left to query it:
                break
            eprint(object_result[object_class_])
            result_remaining_types_to_values = object_result[remaining_types_to_values_]
            result_assigned_types_to_values = object_result[assigned_types_to_values_]
            keys_to_types_list = object_result[keys_to_types_list_]

            is_first_missing_found: bool = False
            for key_to_type_dict in keys_to_types_list:
                arg_key = next(iter(key_to_type_dict))
                arg_type = key_to_type_dict[arg_key]

                if arg_type in result_assigned_types_to_values:
                    eprint(TermColor.DARK_GREEN.value, end = "")
                    eprint(f"{arg_type}:", end = "")
                    eprint(
                        f" {result_assigned_types_to_values[arg_type].arg_value} " +
                        f"[{result_assigned_types_to_values[arg_type].arg_source}]",
                        end = ""
                    )
                    eprint(TermColor.RESET.value, end = "")
                elif arg_type in result_remaining_types_to_values:
                    eprint(TermColor.BRIGHT_YELLOW.value, end = "")
                    if not is_first_missing_found:
                        eprint(f"*{arg_type}:", end = "")
                        is_first_missing_found = True
                    else:
                        eprint(f"{arg_type}:", end = "")
                    eprint(f" ?", end = "")
                    eprint(TermColor.RESET.value, end = "")
                    eprint(
                        f" {'|'.join(result_remaining_types_to_values[arg_type])}",
                        end = ""
                    )
                else:
                    eprint(TermColor.BRIGHT_RED.value, end = "")
                    if not is_first_missing_found:
                        eprint(f"*{arg_type}:", end = "")
                        is_first_missing_found = True
                    else:
                        eprint(f"{arg_type}:", end = "")
                    eprint(f" ?", end = "")
                    eprint(TermColor.RESET.value, end = "")

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
