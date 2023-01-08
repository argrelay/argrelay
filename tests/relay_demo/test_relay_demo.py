from __future__ import annotations

from unittest import TestCase

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.meta_data.ArgSource import ArgSource
from argrelay.meta_data.ArgValue import ArgValue
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.RunMode import RunMode
from argrelay.meta_data.TermColor import TermColor
from argrelay.relay_client import __main__
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.runtime_context.InterpContext import assigned_types_to_values_
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.test_helper import line_no, parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import (
    EnvMockBuilder
)


class ThisTestCase(TestCase):

    def test_propose_auto_comp(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command |", CompType.PrefixHidden, "goto\ndesc\nlist", "Suggest from the set of values for the first unassigned arg type"),

            (line_no(), "some_command goto host dev amer upstream qwer|  ", CompType.PrefixShown, "qwer", "Still as expected with trailing space after cursor"),

            (line_no(), "some_command goto host qa prod|", CompType.SubsequentHelp, "", "Another value from the same dimension with `SubsequentHelp` yet prefix not matching any from other dimensions => no suggestions"),
            (line_no(), "some_command goto host qa amer|", CompType.SubsequentHelp, "amer", "Another value from the same dimension with `SubsequentHelp` and prefix matching some from other dimensions => some suggestions"),


            # TODO: FIXME: Bug: FD-2023-01-07--1: interp skips `upstream` and suggest `downstream` (because there is no `upstream` for `host` and `qa` already pre-selected).
            #       I'm currently thinking about new meta data `ValueScope` with two values `ValueScope.QueriedData` and `ValueScope.EntireValueSpace`.
            #       We should force-assign `upstream` value (but mark it ad `ValueScope.EntireValueSpace`).
            #       * suggested value is incorrect (should be empty)
            #       * description is correct
            (line_no(), "some_command host qa upstream amer qw goto ro service_c green |", CompType.PrefixShown, "downstream", "No more suggestions when all coordinates specified"),

            (line_no(), "some_command host qa goto |", CompType.MenuCompletion, "downstream", "Suggestions for next coordinate are arg values pre-filtered by selection of previous arg values"),

            # TODO: FIXME: Bug: while suggestion on `CompType.PrefixHidden` is filtered, suggestion on `CompType.SubsequentHelp` should be entire value space "dev\nqa\nprod":
            #       This is debatable: what if entire value space is too huge? But then values for huge value space should be ask last allowing to narrow the suggestion down by previous args:
            (line_no(), "some_command upstream goto host |", CompType.PrefixHidden, "dev", ""),
            (line_no(), "some_command upstream goto host |", CompType.SubsequentHelp, "dev", ""),

            # TODO: If selected token left part does not fall into next expected space, suggest from all other (yet not determined) matching that substring.
            (line_no(), "some_command host goto upstream q|", CompType.SubsequentHelp, "qa\nqw\nqwe\nqwer", "Suggestions for subsequent Tab are limited by prefix"),

            # TODO: FIXME: FD-2023-01-07--1: It proposes "dev" while "qa" already specified among args:
            (line_no(), "some_command goto upstream qa apac desc host |", CompType.SubsequentHelp, "dev", ""),

            (line_no(), "some_command service goto upstream|", CompType.PrefixHidden, "upstream", ""),
            (line_no(), "some_command de|", CompType.PrefixHidden, "desc", "Suggest from the set of values for the first unassigned arg type (with matching prefix)"),
            (line_no(), "some_command host goto q| dev", CompType.PrefixHidden, "qwer", "Suggestion for a value from other spaces which do not have coordinate specified"),
            (line_no(), "some_command q| dev", CompType.PrefixHidden, "", "Do not suggest a value from other spaces until they are available for query for current object to search"),
            (line_no(), "some_command pro| dev", CompType.PrefixHidden, "", "No suggestion for another value from a space which already have coordinate specified"),
            (line_no(), "some_command goto service q| whatever", CompType.PrefixHidden, "qa", "Unrecognized value does not obstruct suggestion"),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                env_mock_builder = (
                    EnvMockBuilder()
                    .set_run_mode(RunMode.CompletionMode)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                )
                with env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)

                    actual_suggestions = "\n".join(command_obj.response_dict[arg_values_])
                    self.assertEqual(expected_suggestions, actual_suggestions)

    def test_describe_args(self):
        # @formatter:off
        test_cases = [
            (line_no(), "some_command goto service dev amer upstream sdfg|  ", CompType.DescribeArgs, "sdfg", ""),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                env_mock_builder = (
                    EnvMockBuilder()
                    .set_run_mode(RunMode.CompletionMode)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                )
                with env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    interp_ctx = command_obj.interp_ctx

                    # TODO: Running print again with capturing `stderr`
                    #       (executing end-to-end above generates noise output by server logic).
                    #       A proper implementation would be getting `DescribeArgs`'s response_dict
                    #       and printing it again.
                    with (
                        EnvMockBuilder()
                            .set_mock_mongo_client(False)
                            .set_capture_stderr(True)
                            .build()
                    ):
                        interp_ctx.print_help()

                        self.maxDiff = None
                        # TODO: Fix: currently (after extending data schema)
                        #       what this output shows is entire type list known to static data (it should use limited lists per object)
                        #       and it only compares it to the last `curr_assigned_types_to_values` (while it should print all `assigned_types_to_values_per_object`)
                        self.assertEqual(
                            f"""
ClassFunction
{TermColor.DARK_GREEN.value}ActionType: goto [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}ObjectSelector: service [ExplicitArg]{TermColor.RESET.value}
ClassService
{TermColor.DARK_GREEN.value}CodeMaturity: dev [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}FlowStage: upstream [ExplicitArg]{TermColor.RESET.value}
{TermColor.DARK_GREEN.value}GeoRegion: amer [ExplicitArg]{TermColor.RESET.value}
{TermColor.BRIGHT_YELLOW.value}*HostName: ?{TermColor.RESET.value} qwer
{TermColor.BRIGHT_YELLOW.value}ServiceName: ?{TermColor.RESET.value} service_a
{TermColor.BRIGHT_RED.value}AccessType: ?{TermColor.RESET.value}
{TermColor.BRIGHT_RED.value}ColorTag: ?{TermColor.RESET.value}
""",
                            env_mock_builder.actual_stderr.getvalue()
                        )

    def test_arg_assignments_for_completion(self):
        # @formatter:off
        test_cases = [
            # TODO: uncomment, it works:
            (line_no(), RunMode.CompletionMode, "some_command goto|", CompType.PrefixShown, 0, {GlobalArgType.ActionType.name: None, GlobalArgType.ObjectSelector.name: None}, "No assignment for incomplete token (token pointed by the cursor) in completion mode"),
            (line_no(), RunMode.InvocationMode, "some_command goto|", CompType.PrefixShown, 0, {GlobalArgType.ActionType.name: ArgValue("goto", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "Incomplete token (pointed by the cursor) is complete in invocation mode"),

            (line_no(), RunMode.CompletionMode, "some_command goto |", CompType.PrefixShown, 0, {GlobalArgType.ActionType.name: ArgValue("goto", ArgSource.ExplicitArg), GlobalArgType.ObjectSelector.name: None}, "Explicit assignment for complete token"),
            (line_no(), RunMode.CompletionMode, "some_command goto service |", CompType.PrefixShown, 0, {GlobalArgType.ActionType.name: ArgValue("goto", ArgSource.ExplicitArg), GlobalArgType.ObjectSelector.name: ArgValue("service", ArgSource.ExplicitArg)}, "Explicit assignment for complete token"),

            (line_no(), RunMode.CompletionMode, "some_command goto host prod|", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: None, ServiceArgType.AccessType.name: None}, "No implicit assignment for incomplete token"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host prod|", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment even for incomplete token (token pointed by cursor)"),

            (line_no(), RunMode.CompletionMode, "some_command goto host prod |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"ro\" when code maturity is \"prod\" in completion"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host prod |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("prod", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("ro", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation"),

            (line_no(), RunMode.CompletionMode, "some_command goto host dev |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: None}, "No implicit assignment of access type to \"rw\" when code maturity is \"dev\" in completion"),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            #(line_no(), RunMode.InvocationMode, "some_command goto host dev |", CompType.PrefixShown, 1, {ServiceArgType.CodeMaturity.name: ArgValue("dev", ArgSource.ExplicitArg), ServiceArgType.AccessType.name: ArgValue("rw", ArgSource.ImplicitValue)}, "Implicit assignment of access type to \"rw\" when code maturity is \"uat\" in invocation"),
        ]
        # @formatter:on

        for test_case in test_cases:

            with self.subTest(test_case):
                (
                    line_number,
                    run_mode,
                    test_line,
                    comp_type,
                    found_object_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                env_mock_builder = (
                    EnvMockBuilder()
                    .set_run_mode(run_mode)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                )
                with env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    interp_ctx = command_obj.interp_ctx

                    for arg_type, arg_value in expected_assignments.items():
                        if arg_value is None:
                            self.assertTrue(
                                arg_type not in
                                interp_ctx.assigned_types_to_values_per_object
                                [found_object_ipos]
                                [assigned_types_to_values_]
                            )
                        else:
                            self.assertEqual(
                                arg_value,
                                interp_ctx.assigned_types_to_values_per_object
                                [found_object_ipos]
                                [assigned_types_to_values_]
                                [arg_type]
                            )
