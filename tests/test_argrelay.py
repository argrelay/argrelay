import contextlib
import io
from inspect import currentframe, getframeinfo
from unittest import TestCase

from argrelay.api_ext.relay_server.StaticDataSchema import static_data_desc
from argrelay.api_int.meta_data import CompType, ArgValue, ArgSource, RunMode
from argrelay.relay_client.meta_data import TermColor
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceInterpFactory import ServiceInterpFactory, service_interp_config_desc
from argrelay.relay_server.call_context import ParsedContext, CommandContext
from argrelay.relay_server.line_interp.FirstArgInterpFactory import FirstArgInterpFactory
from argrelay.shared_unit.call_context import InputContext
from relay_server.test_relay_server import load_relay_demo_server_config_dict


def line_no() -> int:
    """
    Get source line in the callee frame
    """
    return getframeinfo(currentframe().f_back).lineno


def parse_line_and_cpos(test_line: str) -> (str, int):
    """
    Translate test line with pipe as cursor place into command line string and cursor char position (cpos)
    """
    assert test_line.count('|') == 1
    cursor_cpos = test_line.index('|')
    command_line = test_line.replace('|', "")
    return command_line, cursor_cpos


def default_test_input_context(command_line: str, cursor_cpos: int) -> InputContext:
    return InputContext(
        command_line = command_line,
        cursor_cpos = cursor_cpos,
        comp_type = CompType.PrefixShown,
        is_debug_enabled = False,
        run_mode = RunMode.CompletionMode,
        comp_key = "0",
    )


def default_test_parsed_context(command_line: str, cursor_cpos: int) -> ParsedContext:
    return ParsedContext.from_instance(
        default_test_input_context(command_line, cursor_cpos),
    )


relay_demo_static_data_object = static_data_desc.from_input_dict(load_relay_demo_server_config_dict()["static_data"])


class ThisTestCase(TestCase):

    def run_coordinate_assignments_tests(self, test_cases, run_mode):
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, test_line, comp_type, expected_assignments, case_comment) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                input_ctx = InputContext(
                    command_line = command_line,
                    cursor_cpos = cursor_cpos,
                    comp_type = comp_type,
                    is_debug_enabled = False,
                    run_mode = run_mode,
                    comp_key = "0",
                )
                parsed_ctx = ParsedContext.from_instance(input_ctx)
                first_arg_vals_to_next_interp_factory_ids = {
                    "some_command": ServiceInterpFactory.__name__,
                }
                config_dict = {
                    "first_arg_vals_to_next_interp_factory_ids": first_arg_vals_to_next_interp_factory_ids,
                }
                interp_factories = {
                    FirstArgInterpFactory.__name__: FirstArgInterpFactory(config_dict = config_dict),
                    ServiceInterpFactory.__name__: ServiceInterpFactory(
                        config_dict = service_interp_config_desc.dict_example,
                    ),
                }
                command_ctx = CommandContext(parsed_ctx, relay_demo_static_data_object, interp_factories)
                command_ctx.interpret_command()
                for arg_type, arg_value in expected_assignments.items():
                    if not arg_value:
                        self.assertTrue(arg_type not in command_ctx.assigned_types_to_values)
                    else:
                        self.assertEqual(arg_value, command_ctx.assigned_types_to_values[arg_type])

    def test_propose_auto_comp(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command prod amer upstream sdfg|  ", CompType.PrefixShown, "sdfg", "Still as expected with trailing space after cursor"),
            (line_no(), "some_command qa prod|", CompType.SubsequentHelp, "", "Another value from the same dimension with `SubsequentHelp` => no suggestions"),
            (line_no(), "some_command qa upstream amer qw list ro |", CompType.PrefixShown, "", "No more suggestions when all coordinates specified"),
            (line_no(), "some_command qa list |", CompType.MenuCompletion, "upstream\ndownstream", "Suggestions for next coordinate show entire space"),
            (line_no(), "some_command upstream goto |", CompType.PrefixHidden, "dev\nqa\nprod", ""),
            (line_no(), "some_command upstream goto |",  CompType.SubsequentHelp, "dev\nqa\nprod", ""),
            # TODO: If selected token left part does not fall into next expected space, suggest from all other (yet not determined) matching that substring.
            (line_no(), "some_command upstream q|", CompType.SubsequentHelp, "qa\nqw\nqwe\nqwer", "Suggestions for subsequent Tab are limited by prefix"),
            (line_no(), "some_command upstream qa apac desc |", CompType.SubsequentHelp, "qw\nqwe\nqwer\nwert\nas\nasd\nasdf\nsdfg\nzx\nzxc\nzxcv\nxcvb", ""),
            (line_no(), "some_command upstream|", CompType.PrefixHidden, "upstream", ""),
            (line_no(), "some_command de|", CompType.PrefixHidden, "desc", "Suggest from the set of values for the first unassigned arg type (with matching prefix)"),
            (line_no(), "some_command q| dev", CompType.PrefixHidden, "qw\nqwe\nqwer", "Suggestion for a value from other spaces which do not have coordinate specified"),
            (line_no(), "some_command pro| dev", CompType.PrefixHidden, "", "No suggestion for another value from a space which already have coordinate specified"),
            (line_no(), "some_command q| whatever", CompType.PrefixHidden, "qa", ""),
            (line_no(), "some_command q|", CompType.PrefixHidden, "qa", ""),
            (line_no(), "some_command |", CompType.PrefixHidden, "goto\ndesc\nlist", "Suggest from the set of values for the first unassigned arg type"),
        ]
        # @formatter:on
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, test_line, comp_type, expected_suggestions, case_comment) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                input_ctx = InputContext(
                    command_line = command_line,
                    cursor_cpos = cursor_cpos,
                    comp_type = comp_type,
                    is_debug_enabled = False,
                    run_mode = RunMode.CompletionMode,
                    comp_key = "0",
                )
                parsed_ctx = ParsedContext.from_instance(input_ctx)
                first_arg_vals_to_next_interp_factory_ids = {
                    "some_command": ServiceInterpFactory.__name__,
                }
                config_dict = {
                    "first_arg_vals_to_next_interp_factory_ids": first_arg_vals_to_next_interp_factory_ids,
                }
                interp_factories = {
                    FirstArgInterpFactory.__name__: FirstArgInterpFactory(config_dict = config_dict),
                    ServiceInterpFactory.__name__: ServiceInterpFactory(
                        config_dict = service_interp_config_desc.dict_example,
                    ),
                }
                command_ctx = CommandContext(parsed_ctx, relay_demo_static_data_object, interp_factories)
                command_ctx.interpret_command()
                actual_suggestions = command_ctx.propose_auto_comp()
                self.assertEqual(expected_suggestions, actual_suggestions)

    def test_describe_args(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command prod amer upstream sdfg|  ", CompType.DescribeArgs, "sdfg", "Still as expected with trailing space after cursor"),
        ]
        # @formatter:on
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, test_line, comp_type, expected_suggestions, case_comment) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                input_ctx = InputContext(
                    command_line = command_line,
                    cursor_cpos = cursor_cpos,
                    comp_type = comp_type,
                    is_debug_enabled = False,
                    run_mode = RunMode.CompletionMode,
                    comp_key = "0",
                )
                parsed_ctx = ParsedContext.from_instance(input_ctx)
                first_arg_vals_to_next_interp_factory_ids = {
                    "some_command": ServiceInterpFactory.__name__,
                }
                config_dict = {
                    "first_arg_vals_to_next_interp_factory_ids": first_arg_vals_to_next_interp_factory_ids,
                }
                interp_factories = {
                    FirstArgInterpFactory.__name__: FirstArgInterpFactory(config_dict = config_dict),
                    ServiceInterpFactory.__name__: ServiceInterpFactory(
                        config_dict = service_interp_config_desc.dict_example,
                    ),
                }
                command_ctx = CommandContext(parsed_ctx, relay_demo_static_data_object, interp_factories)
                command_ctx.interpret_command()
                f = io.StringIO()
                with contextlib.redirect_stderr(f):
                    command_ctx.invoke_action()
                    self.maxDiff = None
                    self.assertEqual(
                        f"""
{TermColor.BRIGHT_YELLOW.value}*ActionType: ?{TermColor.RESET.value} goto|desc|list
{TermColor.DARK_GREEN.value}CodeMaturity: prod [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}FlowStage: upstream [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}GeoRegion: amer [ExplicitArg]{TermColor.RESET.value}
{TermColor.BRIGHT_YELLOW.value}HostName: ?{TermColor.RESET.value} qw|qwe|qwer|wert|as|asd|asdf|sdfg|zx|zxc|zxcv|xcvb
{TermColor.BRIGHT_YELLOW.value}AccessType: ?{TermColor.RESET.value} ro|rw
""",
                        f.getvalue()
                    )

    def test_coordinate_assignments_for_completion(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command prod|", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: None, ServiceArgType.AccessType.name: None}, "No implicit assignment for incomplete token"),
            (line_no(), "some_command prod |", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"ro\" when code maturity is \"prod\" in completion"),
            (line_no(), "some_command dev |", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"rw\" when code maturity is \"uat\" in completion"),
        ]
        # @formatter:on
        self.run_coordinate_assignments_tests(test_cases, RunMode.CompletionMode)

    def test_coordinate_assignments_for_invocation(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command prod|", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment even for incomplete token (token pointed by cursor)"),
            (line_no(), "some_command prod |", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation"),
            (line_no(), "some_command dev |", CompType.PrefixShown, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("rw", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"rw\" when code maturity is \"uat\" in invocation"),
        ]
        # @formatter:on
        self.run_coordinate_assignments_tests(test_cases, RunMode.InvocationMode)
