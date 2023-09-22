from __future__ import annotations

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceDelegator import ServiceDelegator
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.TermColor import TermColor
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import (
    indent_size,
    DescribeLineArgsClientResponseHandler,
)
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.relay_client import __main__
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.test_helper import line_no, parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import (
    EnvMockBuilder,
)
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    # TODO: use unified `verify_output` everywhere
    def verify_assignments(
        self,
        test_data,
        test_line,
        comp_type,
        found_envelope_ipos,
        expected_assignments,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            EnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_test_data_ids_to_load([
                test_data,
            ])
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)
            interp_ctx = command_obj.interp_ctx

            for arg_type, arg_value in expected_assignments.items():
                if arg_value is None:
                    self.assertTrue(
                        arg_type not in
                        interp_ctx.envelope_containers
                        [found_envelope_ipos].assigned_types_to_values
                    )
                else:
                    self.assertEqual(
                        arg_value,
                        interp_ctx.envelope_containers
                        [found_envelope_ipos].assigned_types_to_values
                        [arg_type]
                    )

    # TODO: use unified `verify_output` everywhere
    def run_completion_mode_test(
        self,
        test_data,
        test_line,
        comp_type,
        expected_suggestions,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            EnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_test_data_ids_to_load([
                test_data,
            ])
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)

            actual_suggestions = "\n".join(command_obj.response_dict[arg_values_])
            self.assertEqual(expected_suggestions, actual_suggestions)

    def test_propose_auto_comp_TD_63_37_05_36_demo(self):
        """
        Test arg values suggestion with TD_63_37_05_36 # demo
        """
        # @formatter:off
        test_cases = [
            # TODO: If tangent token left part does not fall into next expected space, in case of `CompType.SubsequentHelp` suggest to specify named arg.

            # TODO: Test that even multiple envelopes can set `ArgSource.ImplicitValue` when one of the arg type has single value among all those envelopes. Add special test data.

            (
                line_no(), "some_command |", CompType.PrefixHidden,
                "help\nintercept\nsubtree\ngoto\ndesc\nlist",
                # TODO: Maybe we should suggest selection for `internal` func like `intercept` as well?
                "Suggest from the set of values for the first unassigned arg type.",
            ),
            (
                line_no(), "some_command goto host dev amer upstream qwer|  ", CompType.PrefixShown,
                "",
                "FS_23_62_89_43: "
                "Host `qwer` is already singled out `data_envelope` "
                "(only one `ServiceEnvelopeClass.ClassHost` within current `ServiceArgType.ClusterName`),"
                "therefore, it is not suggested.",
            ),
            (
                line_no(), "some_command goto host qa prod|", CompType.SubsequentHelp,
                "",
                "Another value from the same dimension with `SubsequentHelp` "
                "yet prefix not matching any from other dimensions => no suggestions",
            ),
            (
                line_no(), "some_command goto host prod apac|", CompType.SubsequentHelp,
                "",
                "FS_23_62_89_43: "
                "`ServiceArgType.CodeMaturity` = `prod` singles out `ServiceEnvelopeClass.ClassCluster` which "
                "skips suggestion for `ServiceArgType.GeoRegion`",
            ),
            (
                line_no(), "some_command host qa upstream amer qw goto ro s_c green rtyu-qu |", CompType.PrefixShown,
                "",
                "No more suggestions when all \"coordinates\" specified",
            ),
            (
                line_no(), "some_command upstream goto host |", CompType.PrefixHidden,
                "dev\nqa\nprod",
                "`PrefixHidden`: arg values for `ClusterName` search is specified ahead function query "
                "but order is \"ignored\"",
            ),
            (
                line_no(), "some_command upstream goto host |", CompType.SubsequentHelp,
                "dev\nqa\nprod",
                "`SubsequentHelp` behaves the same way as `PrefixHidden`",
            ),
            (
                line_no(), "some_command host goto upstream a|", CompType.SubsequentHelp,
                "apac\namer",
                "Suggestions for subsequent Tab are limited by prefix",
            ),
            (
                line_no(),
                "some_command goto upstream dev amer desc host |", CompType.SubsequentHelp,
                "",
                "FS_23_62_89_43: "
                "`ServiceArgType.CodeMaturity` = `dev` and `ServiceArgType.GeoRegion` = `amer` "
                "single out one host and one service, leaving only `ServiceArgType.AccessType` "
                "to be the next to suggest which has a default "
                "leading to no suggestions at all.",
            ),
            (
                line_no(), "some_command service goto upstream|", CompType.PrefixHidden,
                "upstream",
                "",
            ),
            (
                line_no(), "some_command de|", CompType.PrefixHidden,
                "desc",
                "Suggest from the set of values for the first unassigned arg type (with matching prefix)",
            ),
            (
                line_no(), "some_command host goto e| dev", CompType.PrefixHidden,
                "emea",
                "Suggestion for a value from other spaces which do not have \"coordinate\" specified",
            ),
            (
                line_no(), "some_command q| dev", CompType.PrefixHidden,
                "",
                "Do not suggest a value from other spaces until "
                "they are available for query for current envelope to search",
            ),
            (
                line_no(), "some_command pro| dev", CompType.PrefixHidden,
                "",
                "No suggestion for another value from a space which already have \"coordinate\" specified",
            ),
            (
                line_no(), "some_command goto service q| whatever", CompType.PrefixHidden,
                "qa",
                "Unrecognized value does not obstruct suggestion",
            ),
            (
                line_no(), "some_command goto host ip.192.168.1|", CompType.PrefixHidden,
                "ip.192.168.1.1 # zxcv-du\nip.192.168.1.3 # poiu-dd",
                "FS_71_87_33_52: If there are more than one suggestion and help_hint exists, "
                "options are returned with hints",
            ),
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

                self.run_completion_mode_test(
                    "TD_63_37_05_36",  # demo
                    test_line,
                    comp_type,
                    expected_suggestions,
                )

    def test_propose_auto_comp_TD_76_09_29_31_overlapped(self):
        """
        Test arg values suggestion with TD_76_09_29_31 # overlapped
        """

        test_cases = [
            (
                line_no(),
                "some_command host dev goto downstream |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "TD_76_09_29_31: GeoRegion set is suggested (while HostName set is the same)",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "TD_76_09_29_31: HostName set is suggested (while GeoRegion set is the same)",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer am|",
                CompType.PrefixShown,
                ["amer"],
                {},
                None,
                "TD_76_09_29_31 # overlapped: one of the explicit value matches more than one type, "
                "but it is not assigned to all arg types => some suggestion for incomplete missing arg types",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer amer |",
                CompType.PrefixShown,
                [],
                {},
                None,
                "TD_76_09_29_31 # overlapped: all values assigned - no more suggestions",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer amer |",
                CompType.InvokeAction,
                [],
                {
                    0: {
                        GlobalArgType.ObjectSelector.name: AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServiceArgType.GeoRegion.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServiceArgType.FlowStage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServiceArgType.ClusterName.name: AssignedValue("dev-amer-downstream", ArgSource.ImplicitValue),
                        ServiceArgType.HostName.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                    },
                },
                # TODO: add verification of consumed and unconsumed tokens
                ErrorDelegator,
                "TD_76_09_29_31: Both GeoRegion and HostName are correctly assigned",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                    case_comment,
                ) = test_case

                self.verify_output(
                    "TD_76_09_29_31",  # overlapped
                    test_line,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                )

    def test_FS_06_99_43_60_varargs(self):
        """
        Test multiple `data_envelope`-s FS_06_99_43_60 # varargs
        """

        test_cases = [
            (
                line_no(),
                "some_command relay_demo list host dev |",
                CompType.InvokeAction,
                [],
                {},
                # TODO: Make generic validator be able to verify payload (not only `interp_ctx` passed from local client) - JSONPath?
                # {
                #     0: {
                #         GlobalArgType.ActionType.name: AssignedValue("list", ArgSource.ExplicitPosArg),
                #         GlobalArgType.ObjectSelector.name: AssignedValue("host", ArgSource.ExplicitPosArg),
                #     },
                #     1: {
                #         ServiceArgType.HostName.name: "asdf-du",
                #         HostName': "zxcv-du"
                #     },
                #     2: {},
                # },
                # TODO: It works whether there is ErrorDelegator or ServiceDelegator. Why?
                ServiceDelegator,
                "Basic test that list list objects"
            ),
            (
                line_no(),
                "some_command goto service s_b prod |",
                CompType.InvokeAction,
                [],
                {
                    0: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                        GlobalArgType.ObjectSelector.name: AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    1: {},
                    2: {},
                },
                ErrorDelegator,
                "FS_06_99_43_60: Invocation happens with ambiguous services to select - "
                "without narrowing down to single service object",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                    case_comment,
                ) = test_case

                self.verify_output(
                    "TD_63_37_05_36",  # overlapped
                    test_line,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                )

    def test_propose_auto_comp_TD_43_24_76_58_single(self):
        """
        Test arg values suggestion with TD_43_24_76_58 # single
        """

        test_cases = [
            (
                line_no(), "some_command host goto |", CompType.PrefixShown,
                "apac\nemea",
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                },
                "No suggestion of `dev` as all `data_envelope`-s has the same `dev` `ServiceArgType.CodeMaturity`",
            ),
            (
                line_no(), "some_command host goto dev |", CompType.PrefixShown,
                "apac\nemea",
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                },
                "Even if all `data_envelope`-s has the same `dev` `ServiceArgType.CodeMaturity`, "
                "if it is provided, the value `dev` is still consumed."
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    found_envelope_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case

                self.run_completion_mode_test(
                    "TD_43_24_76_58",  # single
                    test_line,
                    comp_type,
                    expected_suggestions,
                )
                self.verify_assignments(
                    "TD_43_24_76_58",
                    test_line,
                    comp_type,
                    found_envelope_ipos,
                    expected_assignments,
                )

    def test_describe_args(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command list service dev upstream amer |", CompType.DescribeArgs,
                "Not only `goto`, also `list` and anything else should work.",
                None,
            ),
            (
                line_no(), "some_command goto service s_b prod qwer-pd-2 |", CompType.DescribeArgs,
                "If current command search results in ambiguous results (more than one `data_envelope`), "
                "it should still work.",
                # TODO: Use generalized validator asserting payload (for this case it is fine) instead of entire stderr output - JSONPath?
                None,
            ),
            (
                line_no(), "some_command |", CompType.DescribeArgs,
                # TODO: FS_41_40_39_44: there must be a special line/field which lists `arg_value`-s based on FS_01_89_09_24 (tree path selecting interp):
                "FS_41_40_39_44: TODO: suggest from tree path.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 6
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external [{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*ActionType: ?{TermColor.reset_style.value} goto desc list 
{" " * indent_size}{TermColor.remaining_value.value}ObjectSelector: ?{TermColor.reset_style.value} host service 
""",
            ),
            (
                line_no(), "some_command goto service dev emea upstream s_|  ", CompType.DescribeArgs,
                # TODO: make another test where set of suggestion listed for tangent token is reduced to those matching this token as prefix (currently selected includes all because all match that prefix).
                "FS_23_62_89_43: tangent token is taken into account in describe.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}emea{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 1
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external [{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ActionType: goto [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ObjectSelector: service [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: 2
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}CodeMaturity: dev [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}FlowStage: upstream [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}GeoRegion: emea [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ClusterName: dev-emea-upstream [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*GroupLabel: ?{TermColor.reset_style.value} aaa sss bbb 
{" " * indent_size}{TermColor.remaining_value.value}ServiceName: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}a{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}b{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}HostName: asdf-du [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}LiveStatus: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}DataCenter: dc.22 [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}IpAddress: ip.172.16.2.1 [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.AccessType.name}: 0
{" " * indent_size}{TermColor.no_option_to_suggest.value}AccessType: [none]{TermColor.reset_style.value}
""",
            ),
            (
                line_no(), "some_command goto host upstream |", CompType.DescribeArgs,
                "Regular description with some props specified (FlowStage) and many still to be narrowed down.",
                # TODO: show differently `[none]` values: those in envelopes which haven't been searched yet, and those which were searched, but no values found in data.
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}host{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 1
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external [{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ActionType: goto [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ObjectSelector: host [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassHost.name}: 10
{" " * indent_size}{TermColor.remaining_value.value}*CodeMaturity: ?{TermColor.reset_style.value} dev qa prod 
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}FlowStage: upstream [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}GeoRegion: ?{TermColor.reset_style.value} apac emea amer 
{" " * indent_size}{TermColor.remaining_value.value}ClusterName: ?{TermColor.reset_style.value} dev-apac-upstream dev-emea-upstream dev-amer-upstream qa-apac-upstream qa-amer-upstream prod-apac-upstream 
{" " * indent_size}{TermColor.remaining_value.value}HostName: ?{TermColor.reset_style.value} zxcv-du asdf-du qwer-du hjkl-qu poiu-qu rtyu-qu rt-qu qwer-pd-1 qwer-pd-3 qwer-pd-2 
{" " * indent_size}{TermColor.remaining_value.value}IpAddress: ?{TermColor.reset_style.value} ip.192.168.1.1 ip.172.16.2.1 ip.192.168.3.1 ip.192.168.4.1 ip.172.16.4.2 ip.192.168.6.1 ip.192.168.6.2 ip.192.168.7.1 ip.192.168.7.2 ip.172.16.7.2 
{ServiceArgType.AccessType.name}: 0
{" " * indent_size}{TermColor.no_option_to_suggest.value}AccessType: [none]{TermColor.reset_style.value}
""",
            ),
            (
                line_no(), "some_command goto service qwer-p|d-1 s_", CompType.DescribeArgs,
                "FS_11_87_76_73: Highlight left part (prefix) of tangent token in description.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} {TermColor.unconsumed_token.value}s_{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 1
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external [{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ActionType: goto [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ObjectSelector: service [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: 2
{" " * indent_size}{TermColor.other_assigned_arg_value.value}CodeMaturity: prod [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FlowStage: upstream [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}GeoRegion: apac [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ClusterName: prod-apac-upstream [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*GroupLabel: ?{TermColor.reset_style.value} aaa sss bbb 
{" " * indent_size}{TermColor.remaining_value.value}ServiceName: ?{TermColor.reset_style.value} s_a s_b 
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}HostName: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}LiveStatus: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}DataCenter: dc.07 [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}IpAddress: ip.192.168.7.1 [{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.AccessType.name}: 0
{" " * indent_size}{TermColor.no_option_to_suggest.value}AccessType: [none]{TermColor.reset_style.value}
""",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    case_comment,
                    stderr_output,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                outer_env_mock_builder = (
                    EnvMockBuilder()
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                    .set_test_data_ids_to_load([
                        "TD_63_37_05_36",  # demo
                    ])
                )
                with outer_env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    interp_ctx = command_obj.interp_ctx

                    if not stderr_output:
                        # Output is not specified - not to be asserted:
                        continue

                    # TODO: Running print again with capturing `stderr`
                    #       (executing end-to-end above generates noise output on stdout by local server logic).
                    #       A proper implementation would be getting `DescribeArgs`'s response_dict
                    #       and printing it again.
                    inner_env_mock_builder = (
                        EnvMockBuilder()
                        .set_mock_mongo_client(False)
                        .set_capture_stderr(True)
                    )
                    with inner_env_mock_builder.build():
                        interp_result: InterpResult = InterpResult(
                            all_tokens = interp_ctx.parsed_ctx.all_tokens,
                            consumed_tokens = interp_ctx.consumed_tokens,
                            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
                            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
                            envelope_containers = interp_ctx.envelope_containers,
                        )
                        DescribeLineArgsClientResponseHandler.render_result(interp_result)

                        self.maxDiff = None
                        self.assertEqual(
                            stderr_output,
                            inner_env_mock_builder.actual_stderr.getvalue()
                        )

    def test_arg_assignments_for_completion(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command goto host dev-emea-downstream |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                    ServiceArgType.GeoRegion.name: AssignedValue("emea", ArgSource.ImplicitValue),
                    ServiceArgType.FlowStage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                    ServiceArgType.ClusterName.name: AssignedValue("dev-emea-downstream", ArgSource.ExplicitPosArg),
                },
                "Implicit assignment of all cluster categories when cluster name is specified",
            ),
            (
                line_no(), "some_command goto host prod-apac-downstream wert-pd-1 |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.AccessType.name: AssignedValue("ro", ArgSource.DefaultValue),
                },
                "Default `ro` for `prod`",
            ),
            (
                line_no(), "some_command goto host prod-apac-downstream wert-pd-1 rw |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.AccessType.name: AssignedValue("rw", ArgSource.ExplicitPosArg),
                },
                "Override default `ro` for `prod` to `rw`",
            ),
            (
                line_no(), "some_command goto host dev-apac-upstream zxcv-du |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.AccessType.name: AssignedValue("rw", ArgSource.DefaultValue),
                },
                "Default `rw` for non-`prod`",
            ),
            (
                line_no(), "some_command goto|", CompType.PrefixShown,
                0,
                {
                    GlobalArgType.ActionType.name: None,
                    GlobalArgType.ObjectSelector.name: None,
                },
                "No assignment for incomplete token (token pointed by the cursor) in completion mode",
            ),
            (
                line_no(), "some_command desc host zxcv|", CompType.PrefixShown,
                0,
                {
                    GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                    GlobalArgType.ActionType.name: AssignedValue("desc", ArgSource.ExplicitPosArg),
                    ServiceArgType.AccessType.name: None,
                },
                "Incomplete token (pointed by the cursor) is complete in invocation mode",
            ),
            (
                line_no(), "some_command goto |", CompType.PrefixShown,
                0,
                {
                    GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                    GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                    GlobalArgType.ObjectSelector.name: None,
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(), "some_command goto service |", CompType.PrefixShown,
                0,
                {
                    GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                    GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                    GlobalArgType.ObjectSelector.name: AssignedValue("service", ArgSource.ExplicitPosArg),
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(), "some_command goto host prod|", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.CodeMaturity.name: None,
                    ServiceArgType.AccessType.name: None,
                },
                "No implicit assignment for incomplete token",
            ),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            # (
            #     line_no(), "some_command goto host prod|", CompType.PrefixShown,
            #     1,
            #     {
            #         ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
            #         ServiceArgType.AccessType.name: AssignedValue("ro", ArgSource.ImplicitValue),
            #     },
            #     "Implicit assignment even for incomplete token (token pointed by cursor)",
            # ),
            (
                line_no(), "some_command goto host prod |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                    ServiceArgType.AccessType.name: None,
                },
                "No implicit assignment of access type to \"ro\" when code maturity is \"prod\" in completion",
            ),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            # (
            #     line_no(), "some_command goto host prod |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
            #         ServiceArgType.AccessType.name: AssignedValue("ro", ArgSource.ImplicitValue),
            #     },
            #     "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation",
            # ),
            (
                line_no(), "some_command goto host dev |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                    ServiceArgType.AccessType.name: None,
                },
                "No implicit assignment of access type to \"rw\" when code maturity is \"dev\" in completion",
            ),
            # TODO: re-implement functionality via data - see `CodeMaturityProcessor`:
            # (
            #     line_no(), "some_command goto host dev |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
            #         ServiceArgType.AccessType.name: AssignedValue("rw", ArgSource.ImplicitValue),
            #     },
            #     "Implicit assignment of access type to \"rw\" when code maturity is \"uat\" in invocation",
            # ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    found_envelope_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case
                self.verify_assignments(
                    "TD_63_37_05_36",
                    test_line,
                    comp_type,
                    found_envelope_ipos,
                    expected_assignments,
                )

    # TODO: generalize and factor out common part in capture_invocation_input_1 and capture_invocation_input_2:
    # TODO: use unified `verify_output` everywhere
    def test_capture_invocation_input_1(self):
        test_line = "some_command goto service prod downstream wert-pd-1 |"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            EnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.InvokeAction)
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
            .set_capture_delegator_invocation_input(ErrorDelegator)
        )
        with env_mock_builder.build():
            __main__.main()
            print(EnvMockBuilder.invocation_input)
            invocation_input = EnvMockBuilder.invocation_input
            self.assertEqual(
                ServiceEnvelopeClass.ClassService.name,
                invocation_input.data_envelopes[1][ReservedArgType.EnvelopeClass.name]
            )
            self.assertEqual(
                "prod-apac-downstream",
                invocation_input.data_envelopes[1][ServiceArgType.ClusterName.name]
            )
            self.assertEqual(
                "wert-pd-1",
                invocation_input.data_envelopes[1][ServiceArgType.HostName.name]
            )
            self.assertEqual(
                "tt1",
                invocation_input.data_envelopes[1][ServiceArgType.ServiceName.name]
            )
            self.assertTrue(True)

    # TODO: generalize and factor out common part in capture_invocation_input_1 and capture_invocation_input_2:
    def test_capture_invocation_input_2(self):
        test_line = "some_command list service dev upstream emea |"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_mock_builder = (
            EnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.InvokeAction)
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
            .set_capture_delegator_invocation_input(ServiceDelegator)
        )
        with env_mock_builder.build():
            __main__.main()
            print(EnvMockBuilder.invocation_input)
            invocation_input = EnvMockBuilder.invocation_input
            # 1st:
            vararg_ipos_0 = 1
            self.assertEqual(
                ServiceEnvelopeClass.ClassService.name,
                invocation_input.data_envelopes[vararg_ipos_0][ReservedArgType.EnvelopeClass.name]
            )
            self.assertEqual(
                "dev-emea-upstream",
                invocation_input.data_envelopes[vararg_ipos_0][ServiceArgType.ClusterName.name]
            )
            self.assertEqual(
                "s_a",
                invocation_input.data_envelopes[vararg_ipos_0][ServiceArgType.ServiceName.name]
            )
            # 2nd:
            vararg_ipos_1 = vararg_ipos_0 + 1
            self.assertEqual(
                ServiceEnvelopeClass.ClassService.name,
                invocation_input.data_envelopes[vararg_ipos_1][ReservedArgType.EnvelopeClass.name]
            )
            self.assertEqual(
                "dev-emea-upstream",
                invocation_input.data_envelopes[vararg_ipos_1][ServiceArgType.ClusterName.name]
            )
            self.assertEqual(
                "s_b",
                invocation_input.data_envelopes[vararg_ipos_1][ServiceArgType.ServiceName.name]
            )
