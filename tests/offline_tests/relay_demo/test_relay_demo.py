from __future__ import annotations

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceDelegator import ServiceDelegator
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.TermColor import TermColor
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import (
    indent_size,
    DescribeLineArgsClientResponseHandler,
)
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.relay_client import __main__
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.test_infra import line_no, parse_line_and_cpos
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
    EmptyEnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

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
                [
                    "config",
                    "desc",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                ],
                # TODO: Maybe we should suggest selection for `internal` func like `intercept` as well?
                "Suggest from the set of values for the first unassigned arg type.",
            ),
            (
                line_no(), "some_command goto host dev amer upstream qwer|  ", CompType.PrefixShown,
                [],
                "FS_23_62_89_43: "
                "Host `qwer` is already singled out `data_envelope` "
                "(only one `ServiceEnvelopeClass.ClassHost` within current `ServiceArgType.cluster_name`),"
                "therefore, it is not suggested.",
            ),
            (
                line_no(), "some_command goto host qa prod|", CompType.SubsequentHelp,
                [],
                "Another value from the same dimension with `SubsequentHelp` "
                "yet prefix not matching any from other dimensions => no suggestions",
            ),
            (
                line_no(), "some_command goto host prod apac|", CompType.SubsequentHelp,
                [],
                "FS_23_62_89_43: "
                "`ServiceArgType.code_maturity` = `prod` singles out `ServiceEnvelopeClass.ClassCluster` which "
                "skips suggestion for `ServiceArgType.geo_region`",
            ),
            (
                line_no(), "some_command host qa upstream amer qw goto ro s_c green rtyu-qu |", CompType.PrefixShown,
                [],
                "No more suggestions when all \"coordinates\" specified",
            ),
            (
                line_no(), "some_command upstream goto host |", CompType.PrefixHidden,
                [
                    "dev",
                    "prod",
                    "qa",
                ],
                "`PrefixHidden`: arg values for `cluster_name` search is specified ahead function query "
                "but order is \"ignored\"",
            ),
            (
                line_no(), "some_command upstream goto host |", CompType.SubsequentHelp,
                [
                    "dev",
                    "prod",
                    "qa",
                ],
                "`SubsequentHelp` behaves the same way as `PrefixHidden`",
            ),
            (
                line_no(), "some_command host goto upstream a|", CompType.SubsequentHelp,
                [
                    "amer",
                    "apac",
                ],
                "Suggestions for subsequent Tab are limited by prefix",
            ),
            (
                line_no(),
                "some_command goto upstream dev amer desc host |", CompType.SubsequentHelp,
                [],
                "FS_23_62_89_43: "
                "`ServiceArgType.code_maturity` = `dev` and `ServiceArgType.geo_region` = `amer` "
                "single out one host and one service, leaving only `ServiceArgType.access_type` "
                "to be the next to suggest which has a default "
                "leading to no suggestions at all.",
            ),
            (
                line_no(), "some_command service goto upstream|", CompType.PrefixHidden,
                [
                    "upstream",
                ],
                "Suggest tangent arg (shell should normally place a space on Tab after the arg to complete the arg).",
            ),
            (
                line_no(), "some_command de|", CompType.PrefixHidden,
                [
                    "desc",
                ],
                "Suggest from the set of values for the first unassigned arg type (with matching prefix)",
            ),
            (
                line_no(), "some_command host goto e| dev", CompType.PrefixHidden,
                [
                    "emea",
                ],
                "FS_13_51_07_97: Suggestion for a value from other spaces which do not have \"coordinate\" specified yet.",
            ),
            (
                line_no(), "some_command q| dev", CompType.PrefixHidden,
                [],
                "Do not suggest a value from other spaces until "
                "they are available for query for current envelope to search",
            ),
            (
                line_no(), "some_command pro| dev", CompType.PrefixHidden,
                [],
                "FS_13_51_07_97: No suggestion for another value from a space which already have \"coordinate\" specified, "
                "and this value still do not force itself (FS_90_48_11_45) yet as it is incomplete.",
            ),
            (
                line_no(), "some_command goto service q| whatever", CompType.PrefixHidden,
                [
                    "qa",
                ],
                "Unrecognized value does not obstruct suggestion.",
            ),
            (
                line_no(), "some_command goto host ip.192.168.1|", CompType.PrefixHidden,
                [
                    "ip.192.168.1.1 # zxcv-du",
                    "ip.192.168.1.3 # poiu-dd",
                ],
                "FS_71_87_33_52: If there are more than one suggestion and help_hint exists, "
                "options are returned with hints",
            ),
            (
                line_no(), "some_command host goto upstream \"x\" a|", CompType.PrefixShown,
                [
                    "amer",
                    "apac",
                ],
                "FS_92_75_93_01: Ensure double quotes (which are used as special char in JSON format) "
                "are at least not causing problem in (A) unconsumed (B) non-tangent arg for (C) local server test.",
            ),
            (
                line_no(), "some_command host goto upstream \"a\"|", CompType.PrefixShown,
                # TODO: Fix this: it has to be "apac\namer":
                [],
                "FS_92_75_93_01: Register bug that double quotes (which are used as special char in JSON format) "
                "are at causing interpretation problem to suggest completion options for tangent arg.",
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

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_18_64_57_18_varargs(self):
        """
        Test multiple `data_envelope`-s FS_18_64_57_18 # varargs
        """

        test_cases = [
            (
                line_no(),
                "some_command list host dev |",
                {
                    0: {
                        # TODO: Use `ExplicitPosArg` for the first arg instead of `InitValue`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("list", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassHost.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                    },
                    2: None,
                },
                ServiceDelegator,
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "zxcv-du",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "zxcv-dd",
                    },
                    3: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "poiu-dd",
                    },
                    4: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "asdf-du",
                    },
                    5: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "xcvb-dd",
                    },
                    6: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "qwer-du",
                    },
                    7: None,
                },
                "FS_18_64_57_18: Basic test that list multiple objects"
            ),
            (
                line_no(),
                "some_command goto service s_b prod |",
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassService.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.service_name.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServiceArgType.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.geo_region.name: AssignedValue("apac", ArgSource.ImplicitValue),
                    },
                    2: {
                        # Nothing is assigned for `ServiceArgType.access_type`, but it exists.
                    },
                    3: None,
                },
                ErrorDelegator,
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.service_name.name: "s_b",
                        ServiceArgType.host_name.name: "qwer-pd-1",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.service_name.name: "s_b",
                        ServiceArgType.host_name.name: "qwer-pd-2",
                    },
                    3: None,
                },
                "FS_18_64_57_18: Invocation happens with ambiguous (multiple) services to select - "
                "without narrowing down to single service object",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    case_comment,
                ) = test_case

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    None,
                    container_ipos_to_expected_assignments,
                    None,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
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
                # TODO_32_99_70_35: Use generalized validator asserting payload (for this case it is fine) instead of entire stdout str - JSONPath?
                None,
            ),
            (
                line_no(), "some_command |", CompType.DescribeArgs,
                # TODO: FS_41_40_39_44: there must be a special line/field which lists `arg_value`-s based on FS_01_89_09_24 (interp tree):
                "FS_41_40_39_44: TODO: suggest from interp tree.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_n.value}33{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*{func_envelope_path_step_prop_name(1)}: ?{TermColor.reset_style.value} config desc duplicates echo enum goto help intercept list 
{" " * indent_size}{TermColor.remaining_value.value}{func_envelope_path_step_prop_name(2)}: ?{TermColor.reset_style.value} commit config desc double_execution echo goto help host intercept list print_with_exit print_with_io_redirect print_with_level repo service tag 
""",
            ),
            (
                line_no(), "some_command goto service dev emea upstream s_|  ", CompType.DescribeArgs,
                # TODO: make another test where set of suggestion listed for tangent token is reduced to those matching this token as prefix (currently selected includes all because all match that prefix).
                "FS_23_62_89_43: tangent token is taken into account in describe.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}emea{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: {TermColor.found_count_n.value}2{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}code_maturity: dev {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}flow_stage: upstream {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}geo_region: emea {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-emea-upstream {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} aaa bbb sss 
{" " * indent_size}{TermColor.remaining_value.value}service_name: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}a{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}b{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}host_name: asdf-du {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.22 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.172.16.2.1 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: [none]{TermColor.reset_style.value}
""",
            ),
            (
                line_no(), "some_command goto host upstream |", CompType.DescribeArgs,
                "Regular description with some props specified (flow_stage) and many still to be narrowed down.",
                # TODO: show differently `[none]` values: those in envelopes which haven't been searched yet, and those which were searched, but no values found in data.
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}host{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(2)}: host {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassHost.name}: {TermColor.found_count_n.value}10{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*code_maturity: ?{TermColor.reset_style.value} dev prod qa 
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}flow_stage: upstream {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}geo_region: ?{TermColor.reset_style.value} amer apac emea 
{" " * indent_size}{TermColor.remaining_value.value}cluster_name: ?{TermColor.reset_style.value} dev-amer-upstream dev-apac-upstream dev-emea-upstream prod-apac-upstream qa-amer-upstream qa-apac-upstream 
{" " * indent_size}{TermColor.remaining_value.value}host_name: ?{TermColor.reset_style.value} asdf-du hjkl-qu poiu-qu qwer-du qwer-pd-1 qwer-pd-2 qwer-pd-3 rt-qu rtyu-qu zxcv-du 
{" " * indent_size}{TermColor.remaining_value.value}ip_address: ?{TermColor.reset_style.value} ip.172.16.2.1 ip.172.16.4.2 ip.172.16.7.2 ip.192.168.1.1 ip.192.168.3.1 ip.192.168.4.1 ip.192.168.6.1 ip.192.168.6.2 ip.192.168.7.1 ip.192.168.7.2 
{ServiceArgType.access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: [none]{TermColor.reset_style.value}
""",
            ),
            (
                line_no(), "some_command goto service qwer-p|d-1 s_", CompType.DescribeArgs,
                "FS_11_87_76_73: Highlight left part (prefix) of tangent token in description.",
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} {TermColor.unconsumed_token.value}s_{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: {TermColor.found_count_n.value}2{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}code_maturity: prod {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}flow_stage: upstream {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}geo_region: apac {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: prod-apac-upstream {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} aaa bbb sss 
{" " * indent_size}{TermColor.remaining_value.value}service_name: ?{TermColor.reset_style.value} s_a s_b 
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}host_name: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.07 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.7.1 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: [none]{TermColor.reset_style.value}
""",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                self.verify_describe_output(test_case)

    def test_arg_assignments_for_completion_on_single_data_envelope(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command goto host dev-emea-downstream |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                    ServiceArgType.geo_region.name: AssignedValue("emea", ArgSource.ImplicitValue),
                    ServiceArgType.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                    ServiceArgType.cluster_name.name: AssignedValue("dev-emea-downstream", ArgSource.ExplicitPosArg),
                },
                "Implicit assignment of all cluster categories when cluster name is specified",
            ),
            (
                line_no(), "some_command goto host prod-apac-downstream wert-pd-1 |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.access_type.name: AssignedValue("ro", ArgSource.DefaultValue),
                },
                "Default `ro` for `prod`",
            ),
            (
                line_no(), "some_command goto host prod-apac-downstream wert-pd-1 rw |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.ExplicitPosArg),
                },
                "Override default `ro` for `prod` to `rw`",
            ),
            (
                line_no(), "some_command goto host dev-apac-upstream zxcv-du |", CompType.PrefixShown,
                2,
                {
                    ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.DefaultValue),
                },
                "Default `rw` for non-`prod`",
            ),
            (
                line_no(), "some_command goto|", CompType.PrefixShown,
                0,
                {
                    # TODO_32_99_70_35: How to specify that some specific props are not assigned?
                },
                "No assignment for incomplete token (token pointed by the cursor) in completion mode",
            ),
            (
                line_no(), "some_command desc host zxcv|", CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue("desc", ArgSource.ExplicitPosArg),
                    f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    ServiceArgType.access_type.name: None,
                },
                # TODO: Test assertion has nothing to do with incomplete token - it asserts first (func) envelope, but not the `zxcv`-related one.
                # TODO: Is "complete in invocation mode" but this is Tab-completion mode:
                "Incomplete token (pointed by the cursor) is complete in invocation mode.",
            ),
            (
                line_no(), "some_command goto |", CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                    f"{func_envelope_path_step_prop_name(2)}": None,
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(), "some_command goto service |", CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                    f"{func_envelope_path_step_prop_name(2)}": AssignedValue("service", ArgSource.ExplicitPosArg),
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(), "some_command goto \"service\" |", CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                    # TODO_32_99_70_35: How to specify that some specific props are not assigned?
                },
                # TODO: Fix this: "service" must be recognized even if in double quotes:
                "FS_92_75_93_01: Register a bug that \"service\" token is not recognized while in double quotes.",
            ),
            (
                line_no(), "some_command goto host prod|", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.code_maturity.name: None,
                    ServiceArgType.access_type.name: None,
                },
                "No implicit assignment for incomplete token",
            ),
            (
                line_no(), "some_command goto host prod |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                    ServiceArgType.access_type.name: None,
                },
                "No implicit assignment of access type to \"ro\" when code maturity is \"prod\" in completion",
            ),
            # TODO: re-implement functionality via data - see `code_maturityProcessor`:
            # (
            #     line_no(), "some_command goto host prod |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServiceArgType.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
            #         ServiceArgType.access_type.name: AssignedValue("ro", ArgSource.ImplicitValue),
            #     },
            #     "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation",
            # ),
            (
                line_no(), "some_command goto host dev |", CompType.PrefixShown,
                1,
                {
                    ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                    ServiceArgType.access_type.name: None,
                },
                "No implicit assignment of access type to \"rw\" when code maturity is \"dev\" in completion",
            ),
            # TODO: re-implement functionality via data - see `code_maturityProcessor`:
            # (
            #     line_no(), "some_command goto host dev |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
            #         ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.ImplicitValue),
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
                    found_container_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case
                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    None,
                    {
                        found_container_ipos: expected_assignments,
                    },
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_arg_assignments_for_completion_on_multiple_data_envelopes(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command goto host prod wert-pd-1|", CompType.DescribeArgs,
                {
                    1: {
                        ServiceArgType.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.host_name.name: AssignedValue("wert-pd-1", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServiceArgType.access_type.name: AssignedValue("ro", ArgSource.DefaultValue),
                    },
                    3: None,
                },
                None,
                "Implicit assignment even for tangent token (token pointed by cursor)",
            ),
            (
                line_no(), "relay_demo goto service tt|", CompType.DescribeArgs,
                {
                    1: {
                        ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                        ServiceArgType.service_name.name: AssignedValue("tt", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.DefaultValue),
                    },
                    3: None,
                },
                None,
                # TODO: Fix this - see FS_80_82_13_35 highlight tangent prefix:
                "FS_80_82_13_35: Current behavior is to make tangent token `ExplicitPosArg` "
                "because it matches `tt` value exactly. However, ideally we want to see exactly the same options "
                "on Alt+Shift+Q as on Tab (see next test).",
            ),
            (
                line_no(), "relay_demo goto service tt|", CompType.PrefixShown,
                None,
                [
                    "tt",
                    "tt1",
                    "tt2",
                ],
                "FS_80_82_13_35: Even because tangent token matches `tt` value exactly, "
                "suggestions on Tab list all matching that prefix, not just `tt`.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    container_ipos_to_expected_assignments,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_invocation_input(self):

        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command goto service prod downstream wert-pd-1 |",
                ErrorDelegator,
                {
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.cluster_name.name: "prod-apac-downstream",
                        ServiceArgType.host_name.name: "wert-pd-1",
                        ServiceArgType.service_name.name: "tt1",
                    },
                },
                "Verify invocation input when ErrorDelegator is used.",
            ),
            (
                line_no(), "some_command list service dev upstream emea |",
                ServiceDelegator,
                {
                    # vararg_ipos + 0
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.cluster_name.name: "dev-emea-upstream",
                        ServiceArgType.service_name.name: "s_a",
                    },
                    # vararg_ipos + 1
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.cluster_name.name: "dev-emea-upstream",
                        ServiceArgType.service_name.name: "s_b",
                    },
                },
                "Verify invocation input with FS_18_64_57_18 varargs when ServiceDelegator is used.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    case_comment,
                ) = test_case
                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    None,
                    None,
                    None,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )


    def test_FS_72_53_55_13_show_non_default_options_data_only(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "relay_demo goto service dev downstream apac poiu-dd |", CompType.DescribeArgs,
                {
                    1: {
                        ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServiceArgType.host_name.name: AssignedValue("poiu-dd", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.DefaultValue),
                    },
                    3: None,
                },
                {
                    2: {
                        ServiceArgType.access_type.name: [
                            "ro",
                            "rw",
                        ],
                    },
                    3: None,
                },
                None,
                "Provide options hidden by `ArgSource.DefaultValue`.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_72_53_55_13_show_non_default_options_print_out_only(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "relay_demo goto service dev downstream apac poiu-dd |", CompType.DescribeArgs,
                "FS_72_53_55_13: shows options hidden by default.",
                f"""
{TermColor.consumed_token.value}relay_demo{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}downstream{TermColor.reset_style.value} {TermColor.consumed_token.value}apac{TermColor.reset_style.value} {TermColor.consumed_token.value}poiu-dd{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: relay_demo {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}code_maturity: dev {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}flow_stage: downstream {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}geo_region: apac {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-apac-downstream {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} hhh rrr 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}service_name: xx {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}host_name: poiu-dd {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.01 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.1.3 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.access_type.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}access_type: rw {TermColor.other_assigned_arg_value.value}[{ArgSource.DefaultValue.name}]{TermColor.reset_style.value} {TermColor.caption_hidden_by_default.value}{DescribeLineArgsClientResponseHandler.default_overrides_caption}:{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}ro{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}rw{TermColor.reset_style.value} 
""",
            ),
            (
                line_no(), "relay_demo goto service dev downstream apac poiu-dd r|", CompType.DescribeArgs,
                "FS_72_53_55_13: shows `ro` option hidden by default and FS_11_87_76_73 highlights them by prefix.",
                f"""
{TermColor.consumed_token.value}relay_demo{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}downstream{TermColor.reset_style.value} {TermColor.consumed_token.value}apac{TermColor.reset_style.value} {TermColor.consumed_token.value}poiu-dd{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}elay_demo{TermColor.reset_style.value} {TermColor.other_assigned_arg_value.value}[{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.ClassService.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}code_maturity: dev {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}flow_stage: downstream {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}geo_region: apac {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-apac-downstream {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} hhh {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}rr{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}service_name: xx {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}host_name: poiu-dd {TermColor.explicit_pos_arg_value.value}[{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: [none]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.01 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.1.3 {TermColor.other_assigned_arg_value.value}[{ArgSource.ImplicitValue.name}]{TermColor.reset_style.value}
{ServiceArgType.access_type.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}access_type: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}w{TermColor.reset_style.value} {TermColor.other_assigned_arg_value.value}[{ArgSource.DefaultValue.name}]{TermColor.reset_style.value} {TermColor.caption_hidden_by_default.value}{DescribeLineArgsClientResponseHandler.default_overrides_caption}:{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}o{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}w{TermColor.reset_style.value} 
""",
            ),
            # {TermColor.value_hidden_by_default.value}ro{TermColor.reset_style.value}
            # {TermColor.value_hidden_by_default.value}rw{TermColor.reset_style.value}
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                self.verify_describe_output(test_case)

    def verify_describe_output(
        self,
        test_case,
    ):
        (
            line_number,
            test_line,
            comp_type,
            case_comment,
            stdout_str,
        ) = test_case
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        outer_env_mock_builder = (
            LocalClientEnvMockBuilder()
            .set_reset_local_server(False)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(comp_type)
            .set_test_data_ids_to_load([
                self.__class__.same_test_data_per_class,
            ])
        )
        with outer_env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)
            interp_ctx = command_obj.interp_ctx

            if not stdout_str:
                # Output is not specified - not to be asserted:
                return

            # TODO: Running print again with capturing `stdout`.
            #       Executing end-to-end above may generate
            #       noise output on `stdout`/`stderr` by local server logic.
            #       A proper implementation would probably be intercepting `DescribeArgs`'s response_dict
            #       and printing it separately (when no other logic with extra output can intervene)
            #       to assert the output.
            #       Alternatively, run this test via `RemoteClient` (see `RemoteTestClass`) where output
            #       of the server is not captured (as it is a separate process).
            inner_env_mock_builder = (
                EmptyEnvMockBuilder()
                .set_capture_stdout(True)
                .set_capture_stderr(True)
            )
            with inner_env_mock_builder.build():
                interp_result: InterpResult = InterpResult(
                    arg_values = interp_ctx.comp_suggestions,
                    all_tokens = interp_ctx.parsed_ctx.all_tokens,
                    consumed_tokens = interp_ctx.consumed_tokens,
                    tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
                    tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
                    envelope_containers = interp_ctx.envelope_containers,
                )
                DescribeLineArgsClientResponseHandler.render_result(interp_result)

                self.assertEqual(
                    stdout_str,
                    inner_env_mock_builder.actual_stdout.getvalue(),
                )

                self.assertEqual(
                    "",
                    inner_env_mock_builder.actual_stderr.getvalue(),
                )
