from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_api_server_cli.schema_response.InterpResult import InterpResult
from argrelay_app_client.client_command_local.ClientCommandLocal import (
    ClientCommandLocal,
)
from argrelay_app_client.handler_response.ClientResponseHandlerDescribeLineArgs import (
    ClientResponseHandlerDescribeLineArgs,
    indent_size,
)
from argrelay_app_client.relay_client import __main__
from argrelay_app_server.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_root.enum_desc.TermColor import TermColor
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorError import (
    DelegatorError,
)
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    func_envelope_path_step_prop_name,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceHostGoto import (
    func_id_goto_host_,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceHostList import (
    DelegatorServiceHostList,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceInstanceGoto import (
    func_id_goto_service_,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceInstanceList import (
    DelegatorServiceInstanceList,
)
from argrelay_lib_server_plugin_demo.demo_service.ServiceEnvelopeClass import (
    ServiceEnvelopeClass,
)
from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_test_infra.test_infra import (
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EmptyEnvMockBuilder,
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_propose_auto_comp_TD_63_37_05_36_demo(self):
        """
        Test `arg_value`-s suggestion with TD_63_37_05_36 # demo
        """
        test_cases = [
            # TODO: Test that even multiple envelopes can set `ValueSource.implicit_value` when one of the `prop_name` has single `prop_value` among all those envelopes. Add special test data.
            (
                line_no(),
                "some_command |",
                CompType.PrefixHidden,
                [
                    "config",
                    "data",
                    "desc",
                    "diff",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "no_data",
                    "ssh",
                ],
                "Suggest from the set of values for the first unassigned `prop_name`.",
            ),
            (
                line_no(),
                "some_command goto host dev amer upstream qwer|  ",
                CompType.PrefixShown,
                [],
                "FS_23_62_89_43: `tangent_token` "
                "Host `qwer` is already singled out `data_envelope` "
                "(only one `ServiceEnvelopeClass.class_host` within current `ServicePropName.cluster_name`),"
                "therefore, it is not suggested.",
            ),
            (
                line_no(),
                "some_command goto host qa prod|",
                CompType.SubsequentHelp,
                [],
                "Another value from the same dimension with `SubsequentHelp` "
                "yet prefix not matching any from other dimensions => no suggestions",
            ),
            (
                line_no(),
                "some_command goto host prod apac|",
                CompType.SubsequentHelp,
                [],
                "FS_23_62_89_43: `tangent_token` "
                "`ServicePropName.code_maturity` = `prod` singles out `ServiceEnvelopeClass.class_cluster` which "
                "skips suggestion for `ServicePropName.geo_region`",
            ),
            (
                line_no(),
                "some_command host qa upstream amer qw goto ro s_c green rtyu-qu |",
                CompType.PrefixShown,
                [],
                'No more suggestions when all "coordinates" specified',
            ),
            (
                line_no(),
                "some_command upstream goto host |",
                CompType.PrefixHidden,
                [
                    "dev",
                    "prod",
                    "qa",
                ],
                "`PrefixHidden`: `prop_value`-s for `cluster_name` search is specified ahead function query "
                'but order is "ignored"',
            ),
            (
                line_no(),
                "some_command upstream goto host |",
                CompType.SubsequentHelp,
                [
                    "dev",
                    "prod",
                    "qa",
                ],
                "`SubsequentHelp` behaves the same way as `PrefixHidden`",
            ),
            (
                line_no(),
                "some_command host goto upstream a|",
                CompType.SubsequentHelp,
                [
                    "amer",
                    "apac",
                ],
                "Suggestions for subsequent Tab are limited by prefix",
            ),
            (
                line_no(),
                "some_command goto upstream dev amer desc host |",
                CompType.SubsequentHelp,
                [],
                "FS_23_62_89_43: `tangent_token` "
                "`ServicePropName.code_maturity` = `dev` and `ServicePropName.geo_region` = `amer` "
                "single out one host and one service, leaving only `ServicePropName.access_type` "
                "to be the next to suggest which has a default "
                "leading to no suggestions at all.",
            ),
            (
                line_no(),
                "some_command service goto upstream|",
                CompType.PrefixHidden,
                [
                    "upstream",
                ],
                "Suggest tangent arg (shell should normally place a space on Tab after the arg to complete the arg).",
            ),
            (
                line_no(),
                "some_command de|",
                CompType.PrefixHidden,
                [
                    "desc",
                ],
                "Suggest from the set of values for the first unassigned `prop_name` (with matching prefix)",
            ),
            (
                line_no(),
                "some_command host goto e| dev",
                CompType.PrefixHidden,
                [
                    "emea",
                ],
                'FS_13_51_07_97: Suggestion for a value from other spaces which do not have "coordinate" specified yet.',
            ),
            (
                line_no(),
                "some_command pro|",
                CompType.PrefixHidden,
                [],
                "Do not suggest a value (prod) from other spaces until "
                "they are available for query for next envelope to search (current one is func).",
            ),
            (
                line_no(),
                "some_command goto host pro| dev",
                CompType.PrefixHidden,
                [],
                "FS_13_51_07_97: No suggestion for another value `prod` from a space which "
                'already have "coordinate" `dev` specified.',
            ),
            (
                line_no(),
                "some_command goto service q| whatever",
                CompType.PrefixHidden,
                [
                    "qa",
                ],
                "Unrecognized value does not obstruct suggestion.",
            ),
            (
                line_no(),
                "some_command goto host ip.192.168.1|",
                CompType.PrefixHidden,
                [
                    "ip.192.168.1.1 # zxcv-du",
                    "ip.192.168.1.3 # poiu-dd",
                ],
                "FS_71_87_33_52: If there are more than one suggestion and help_hint exists, "
                "options are returned with hints",
            ),
            (
                line_no(),
                'some_command host goto upstream "x" a|',
                CompType.PrefixShown,
                [
                    "amer",
                    "apac",
                ],
                "FS_92_75_93_01: Ensure double quotes (which are used as special char in JSON format) "
                "are at least not causing problem in (A) remaining (B) non-tangent arg for (C) local server test.",
            ),
            (
                line_no(),
                'some_command host goto upstream "a"|',
                CompType.PrefixShown,
                # TODO: Fix this: it has to be "apac\namer":
                [],
                "FS_92_75_93_01: Register bug that double quotes (which are used as special char in JSON format) "
                "are at causing interpretation problem to suggest completion options for tangent arg.",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer amer|",
                CompType.PrefixShown,
                [],
                "Step 1: No suggestions because FS_23_62_89_43 `tangent_token`narrows down selection to 0 options.",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer amer |",
                CompType.PrefixShown,
                ["apac", "emea"],
                "Step 2: Some suggestions exists because FS_23_62_89_43 `tangent_token` is not present and "
                "the logic skips remaining args suggesting what is missing for the next `prop_name`. ",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
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
                [
                    "downstream",
                    "upstream",
                ],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "list",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_host.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue(
                            "dev", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: None,
                },
                DelegatorServiceHostList,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "zxcv-du",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "zxcv-dd",
                    },
                    3: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "poiu-dd",
                    },
                    4: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "asdf-du",
                    },
                    5: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "xcvb-dd",
                    },
                    6: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "qwer-du",
                    },
                    7: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: None,
                },
                "FS_18_64_57_18: Basic test that list multiple objects",
            ),
            (
                line_no(),
                "some_command list service s_b prod |",
                [
                    "bbb",
                    "sss",
                    "xxx",
                ],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "list",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "service",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_service.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.service_name.name: AssignedValue(
                            "s_b", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.code_maturity.name: AssignedValue(
                            "prod", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.geo_region.name: AssignedValue(
                            "apac", ValueSource.implicit_value
                        ),
                    },
                    2: None,
                },
                DelegatorServiceInstanceList,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "s_b",
                        ServicePropName.host_name.name: "qwer-pd-1",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "s_b",
                        ServicePropName.host_name.name: "qwer-pd-2",
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: None,
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
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_97_64_39_94_token_buckets(self):
        """
        Test how FS_97_64_39_94 `token_bucket`-s are used by `envelope_container`-s
        """

        test_cases = [
            (
                line_no(),
                "% some_command % list host % dev |",
                [
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       This suggestion list does not make sense
                    #       (at least for this position of the cursor).
                    #       Fix FS_01_89_09_24 interp tree interp to suggest anything only
                    #       when cursor is in the first `token_bucket` (ipos = 0).
                    "ar_ssh",
                    "argrelay.check_env",
                    "lay",
                    "relay_demo",
                    "service_relay_demo",
                    "some_command",
                ],
                {
                    0: None,
                },
                DelegatorError,
                {
                    0: None,
                },
                {
                    0: None,
                },
                "FS_97_64_39_94: Case A1: `token_bucket` before the one with `some_command` is not consumed by anything "
                "because it is empty - this causes FS_01_89_09_24 interp tree interp consume nothing via tree path. "
                "So no progress can be made beyond the first `token_bucket` (ipos = 0).",
            ),
            (
                line_no(),
                "some_command % list host % dev |",
                [
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       This suggestion list does not make sense
                    #       (at least for this position of the cursor).
                    #       Such suggestion makes sense only in the `token_bucket` with ipos = 0.
                    "config",
                    "data",
                    "desc",
                    "diff",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "no_data",
                    "ssh",
                ],
                {},
                DelegatorError,
                {
                    0: None,
                },
                None,
                "FS_97_64_39_94: Case A2: `token_bucket` with `some_command` is not used by any `envelope_container`, "
                "because it is consumed only by FS_01_89_09_24 interp tree interp (via tree path without data query). "
                "So no progress can be made beyond the first `token_bucket` (ipos = 0).",
            ),
            (
                line_no(),
                "some_command list host % dev |",
                [
                    "downstream",
                    "upstream",
                ],
                None,
                DelegatorServiceHostList,
                None,
                {
                    0: 0,
                    1: 1,
                    2: None,
                },
                "FS_97_64_39_94: Case A3: `token_bucket` with `some_command` is consumed by both"
                "FS_01_89_09_24 interp tree interp (via tree path without data query) and "
                "FS_26_43_73_72 func tree into `envelope_container`-s via data query - "
                "the rest of `token_bucket`-s are consumed by func tree as func args.",
            ),
            (
                line_no(),
                "some_command list service % SOME_UNKNOWN_VALUE % s_b prod |",
                [
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       This suggestion list does not make sense
                    #       (at least for this position of the cursor).
                    #       Such suggestion makes sense only in the `token_bucket` corresponding to service selection.
                    "dev",
                    "prod",
                    "qa",
                ],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "list",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "service",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_service.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.service_name.name: None,
                        ServicePropName.code_maturity.name: None,
                        ServicePropName.geo_region.name: None,
                    },
                    2: None,
                },
                DelegatorServiceInstanceList,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                    },
                    # Multiple other `data_envelope`-s...
                },
                {
                    0: 0,
                    1: 1,
                    2: None,
                },
                "FS_97_64_39_94: `token_bucket` with SOME_UNKNOWN_VALUE is not used",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_describe_args(self):
        test_cases = [
            (
                line_no(),
                "some_command list service dev upstream amer |",
                CompType.DescribeArgs,
                "Not only `goto`, also `list` and anything else should work.",
                None,
            ),
            (
                line_no(),
                "some_command goto service s_b prod qwer-pd-2 |",
                CompType.DescribeArgs,
                "If current command search results in ambiguous results (more than one `data_envelope`), "
                "it should still work.",
                # TODO: TODO_32_99_70_35: Use generalized validator asserting payload (for this case it is fine) instead of entire stdout str - JSONPath?
                None,
            ),
            (
                line_no(),
                "some_command |",
                CompType.DescribeArgs,
                # TODO: FS_41_40_39_44: There must be a special line/field which lists `arg_value`-s based on FS_01_89_09_24 (interp tree) or maybe not? Not because interp tree path is part of the func lookup anyway:
                "FS_41_40_39_44: TODO: suggest from interp tree.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_n.value}43{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*{func_envelope_path_step_prop_name(1)}: ?{TermColor.reset_style.value} config data desc diff duplicates echo enum goto help intercept list no_data ssh 
{" " * indent_size}{TermColor.remaining_value.value}{func_envelope_path_step_prop_name(2)}: ?{TermColor.reset_style.value} commit config data desc diff double_execution echo get goto help host intercept list no_data print_with_exit print_with_io_redirect print_with_level repo service set ssh tag {SpecialChar.NoPropValue.value} 
{" " * indent_size}{TermColor.remaining_value.value}{func_envelope_path_step_prop_name(3)}: ?{TermColor.reset_style.value} commit double_execution get host print_with_exit print_with_io_redirect print_with_level repo service set tag {SpecialChar.NoPropValue.value} 
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_state.name}: ?{TermColor.reset_style.value} {FuncState.fs_alpha} {FuncState.fs_beta} {FuncState.fs_demo} {FuncState.fs_gamma} {FuncState.fs_ignorable} 
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_id.name}: ?{TermColor.reset_style.value} func_id_desc_git_commit func_id_desc_git_tag func_id_desc_host func_id_desc_service func_id_diff_service func_id_double_execution func_id_echo_args func_id_get_data_envelopes func_id_goto_git_repo func_id_goto_host func_id_goto_service func_id_help_hint func_id_intercept_invocation func_id_list_host func_id_list_service func_id_no_data func_id_print_with_exit_code func_id_print_with_io_redirect func_id_print_with_severity_level func_id_query_enum_items func_id_set_data_envelopes func_id_ssh_dst 
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto service dev emea upstream s_|  ",
                CompType.DescribeArgs,
                # TODO: make another test where set of suggestion listed for `tangent_token` is reduced to those matching this token as prefix (currently selected includes all because all match that prefix).
                "FS_23_62_89_43: `tangent_token` is taken into account in describe.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}emea{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_n.value}2{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}code_maturity: dev {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}flow_stage: upstream {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}geo_region: emea {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-emea-upstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} aaa bbb sss 
{" " * indent_size}{TermColor.remaining_value.value}service_name: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}a{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s_{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}b{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}host_name: asdf-du {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.22 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.172.16.2.1 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}{ReservedPropName.envelope_class.name}: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto host upstream |",
                CompType.DescribeArgs,
                "Regular description with some props specified (flow_stage) and many still to be narrowed down.",
                # TODO: show differently `{SpecialChar.NoPropValue.value}` values: those in envelopes which haven't been searched yet, and those which were searched, but no values found in data.
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}host{TermColor.reset_style.value} {TermColor.consumed_token.value}upstream{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: host {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_host_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_host.name}: {TermColor.found_count_n.value}10{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_host.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*code_maturity: ?{TermColor.reset_style.value} dev prod qa 
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}flow_stage: upstream {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}geo_region: ?{TermColor.reset_style.value} amer apac emea 
{" " * indent_size}{TermColor.remaining_value.value}cluster_name: ?{TermColor.reset_style.value} dev-amer-upstream dev-apac-upstream dev-emea-upstream prod-apac-upstream qa-amer-upstream qa-apac-upstream 
{" " * indent_size}{TermColor.remaining_value.value}host_name: ?{TermColor.reset_style.value} asdf-du hjkl-qu poiu-qu qwer-du qwer-pd-1 qwer-pd-2 qwer-pd-3 rt-qu rtyu-qu zxcv-du 
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}ip_address: ?{TermColor.reset_style.value} ip.172.16.2.1 ip.172.16.4.2 ip.172.16.7.2 ip.192.168.1.1 ip.192.168.3.1 ip.192.168.4.1 ip.192.168.6.1 ip.192.168.6.2 ip.192.168.7.1 ip.192.168.7.2 
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}{ReservedPropName.envelope_class.name}: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto service qwer-p|d-1 s_",
                CompType.DescribeArgs,
                "FS_11_87_76_73: Highlight `token_left_part` (prefix) of `tangent_token` in description.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} {TermColor.remaining_token.value}s_{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_n.value}2{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}code_maturity: prod {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}flow_stage: upstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}geo_region: apac {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: prod-apac-upstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} aaa bbb sss 
{" " * indent_size}{TermColor.remaining_value.value}service_name: ?{TermColor.reset_style.value} s_a s_b 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}host_name: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}qwer-p{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}d-1{TermColor.reset_style.value} {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.07 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.7.1 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}{ReservedPropName.envelope_class.name}: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
""",
                # fmt: on
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                self.verify_describe_output(test_case)

    def test_arg_assignments_for_completion_on_single_data_envelope(self):
        test_cases = [
            (
                line_no(),
                "some_command goto host dev-emea-downstream |",
                CompType.PrefixShown,
                1,
                {
                    ServicePropName.code_maturity.name: AssignedValue(
                        "dev", ValueSource.implicit_value
                    ),
                    ServicePropName.geo_region.name: AssignedValue(
                        "emea", ValueSource.implicit_value
                    ),
                    ServicePropName.flow_stage.name: AssignedValue(
                        "downstream", ValueSource.implicit_value
                    ),
                    ServicePropName.cluster_name.name: AssignedValue(
                        "dev-emea-downstream",
                        ValueSource.explicit_offered_arg,
                    ),
                },
                "Implicit assignment of all cluster categories when cluster name is specified",
            ),
            (
                line_no(),
                "some_command goto host prod-apac-downstream wert-pd-1 |",
                CompType.PrefixShown,
                2,
                {
                    ServicePropName.access_type.name: AssignedValue(
                        "ro", ValueSource.default_value
                    ),
                },
                "Default `ro` for `prod`",
            ),
            (
                line_no(),
                "some_command goto host prod-apac-downstream wert-pd-1 rw |",
                CompType.PrefixShown,
                2,
                {
                    ServicePropName.access_type.name: AssignedValue(
                        "rw", ValueSource.explicit_offered_arg
                    ),
                },
                "Override default `ro` for `prod` to `rw`",
            ),
            (
                line_no(),
                "some_command goto host dev-apac-upstream zxcv-du |",
                CompType.PrefixShown,
                2,
                {
                    ServicePropName.access_type.name: AssignedValue(
                        "rw", ValueSource.default_value
                    ),
                },
                "Default `rw` for non-`prod`",
            ),
            (
                line_no(),
                "some_command goto|",
                CompType.PrefixShown,
                0,
                {
                    # TODO: TODO_32_99_70_35: How to specify that some specific props are not assigned?
                },
                "No assignment for `incomplete_token` (token pointed by the cursor) in completion mode",
            ),
            (
                line_no(),
                "some_command desc host zxcv|",
                CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                        "some_command", ValueSource.init_value
                    ),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                        "desc", ValueSource.explicit_offered_arg
                    ),
                    f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                        "host", ValueSource.explicit_offered_arg
                    ),
                    ServicePropName.access_type.name: None,
                },
                # TODO: Test assertion has nothing to do with `incomplete_token` - it asserts first (func) envelope, but not the `zxcv`-related one.
                # TODO: Is "complete in invocation mode" but this is Tab-completion mode:
                "`incomplete_token` (pointed by the cursor) is complete in invocation mode.",
            ),
            (
                line_no(),
                "some_command goto |",
                CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                        "some_command", ValueSource.init_value
                    ),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                        "goto", ValueSource.explicit_offered_arg
                    ),
                    f"{func_envelope_path_step_prop_name(2)}": None,
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(),
                "some_command goto service |",
                CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                        "some_command", ValueSource.init_value
                    ),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                        "goto", ValueSource.explicit_offered_arg
                    ),
                    f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                        "service",
                        ValueSource.explicit_offered_arg,
                    ),
                },
                "Explicit assignment for complete token",
            ),
            (
                line_no(),
                'some_command goto "service" |',
                CompType.PrefixShown,
                0,
                {
                    f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                        "some_command", ValueSource.init_value
                    ),
                    f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                        "goto", ValueSource.explicit_offered_arg
                    ),
                    # TODO: TODO_32_99_70_35: How to specify that some specific props are not assigned?
                },
                # TODO: Fix this: "service" must be recognized even if in double quotes:
                'FS_92_75_93_01: Register a bug that "service" token is not recognized while in double quotes.',
            ),
            (
                line_no(),
                "some_command goto host prod|",
                CompType.PrefixShown,
                1,
                {
                    ServicePropName.code_maturity.name: None,
                    ServicePropName.access_type.name: None,
                },
                "No implicit assignment for `incomplete_token`",
            ),
            (
                line_no(),
                "some_command goto host prod |",
                CompType.PrefixShown,
                1,
                {
                    ServicePropName.code_maturity.name: AssignedValue(
                        "prod", ValueSource.explicit_offered_arg
                    ),
                    ServicePropName.access_type.name: None,
                },
                'No implicit assignment of access type to "ro" when code maturity is "prod" in completion',
            ),
            # TODO: re-implement functionality via data - see `code_maturityProcessor`:
            # (
            #     line_no(), "some_command goto host prod |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServicePropName.code_maturity.name: AssignedValue("prod", ValueSource.explicit_offered_arg),
            #         ServicePropName.access_type.name: AssignedValue("ro", ValueSource.implicit_value),
            #     },
            #     "Implicit assignment of access type to \"ro\" when code maturity is \"prod\" in invocation",
            # ),
            (
                line_no(),
                "some_command goto host dev |",
                CompType.PrefixShown,
                1,
                {
                    ServicePropName.code_maturity.name: AssignedValue(
                        "dev", ValueSource.explicit_offered_arg
                    ),
                    ServicePropName.access_type.name: None,
                },
                'No implicit assignment of access type to "rw" when code maturity is "dev" in completion',
            ),
            # TODO: re-implement functionality via data - see `code_maturityProcessor`:
            # (
            #     line_no(), "some_command goto host dev |", CompType.PrefixShown,
            #     1,
            #     {
            #         ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
            #         ServicePropName.access_type.name: AssignedValue("rw", ValueSource.implicit_value),
            #     },
            #     "Implicit assignment of access type to \"rw\" when code maturity is \"uat\" in invocation",
            # ),
        ]

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
                self.verify_output_via_local_client(
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
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_arg_assignments_for_completion_on_multiple_data_envelopes(self):
        test_cases = [
            (
                line_no(),
                "some_command goto host prod wert-pd-1|",
                CompType.DescribeArgs,
                {
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue(
                            "prod", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.host_name.name: AssignedValue(
                            "wert-pd-1", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: {
                        ServicePropName.access_type.name: AssignedValue(
                            "ro", ValueSource.default_value
                        ),
                    },
                    3: None,
                },
                None,
                "Implicit assignment even for tangent token (token pointed by cursor)",
            ),
            (
                line_no(),
                "some_command goto service tt|",
                CompType.DescribeArgs,
                {
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue(
                            "dev", ValueSource.implicit_value
                        ),
                        ServicePropName.service_name.name: AssignedValue(
                            "tt", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: {
                        ServicePropName.access_type.name: AssignedValue(
                            "rw", ValueSource.default_value
                        ),
                    },
                    3: None,
                },
                None,
                # TODO: Fix this - see FS_80_82_13_35 highlight tangent prefix:
                "FS_80_82_13_35: Current behavior is to make tangent token `explicit_offered_arg` "
                "because it matches `tt` value exactly. However, ideally we want to see exactly the same options "
                "on Alt+Shift+Q as on Tab (see next test).",
            ),
            (
                line_no(),
                "some_command goto service tt|",
                CompType.PrefixShown,
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
                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_invocation_input(self):

        test_cases = [
            (
                line_no(),
                "some_command goto service prod downstream wert-pd-1 |",
                DelegatorError,
                {
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.cluster_name.name: "prod-apac-downstream",
                        ServicePropName.host_name.name: "wert-pd-1",
                        ServicePropName.service_name.name: "tt1",
                    },
                },
                f"Verify invocation input when `{DelegatorError.__name__}` is used.",
            ),
            (
                line_no(),
                "some_command list service dev upstream emea |",
                DelegatorServiceInstanceList,
                {
                    # vararg_ipos + 0
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.cluster_name.name: "dev-emea-upstream",
                        ServicePropName.service_name.name: "s_a",
                    },
                    # vararg_ipos + 1
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.cluster_name.name: "dev-emea-upstream",
                        ServicePropName.service_name.name: "s_b",
                    },
                },
                f"Verify invocation input with FS_18_64_57_18 varargs "
                f"when `{DelegatorServiceInstanceList.__name__}` is used.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    case_comment,
                ) = test_case
                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    None,
                    None,
                    None,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_72_53_55_13_show_non_default_options_data_only_with_FS_97_64_39_94_token_buckets(
        self,
    ):
        """
        Test all 3 working together:
        *   FS_72_40_53_00 fill control
        *   FS_72_53_55_13 options hidden by default
        *   FS_97_64_39_94 `token_bucket`
        """
        test_cases = [
            (
                line_no(),
                "some_command goto service dev downstream apac poiu-dd |",
                CompType.DescribeArgs,
                {
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue(
                            "dev", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.host_name.name: AssignedValue(
                            "poiu-dd", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: {
                        ServicePropName.access_type.name: AssignedValue(
                            "rw", ValueSource.default_value
                        ),
                    },
                    3: None,
                },
                {
                    2: {
                        ServicePropName.access_type.name: [
                            "ro",
                            "rw",
                        ],
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: 0,
                },
                f"Ensure options hidden by `{ValueSource.default_value.name}` for `{ServicePropName.access_type.name}` "
                f"and `{EnvelopeContainer.used_token_bucket}` stays None.",
            ),
            (
                line_no(),
                "some_command diff % prod downstream rrr tt1 % passive tt1 |",
                CompType.DescribeArgs,
                {
                    1: {
                        ServicePropName.run_mode.name: AssignedValue(
                            "active", ValueSource.default_value
                        ),
                    },
                    2: {
                        ServicePropName.run_mode.name: AssignedValue(
                            "passive", ValueSource.explicit_offered_arg
                        ),
                    },
                    3: None,
                },
                {
                    1: {
                        ServicePropName.run_mode.name: [
                            "active",
                            "passive",
                        ],
                    },
                    2: {
                        # Ensure there is nothing hidden by default
                        # (because there is no `ValueSource.default_value`, but `ValueSource.explicit_offered_arg` instead)
                        ServicePropName.run_mode.name: None,
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 1,
                    2: 2,
                },
                "Case A1: "
                "FS_97_64_39_94 `token_bucket`-s used by the 1st/left service `envelope_container` prevents assignment "
                "of `ServicePropName.run_mode` = `passive` specified for the 2nd/right service `envelope_container`. "
                "In other words, 1st/left service `envelope_container` still uses default, not override, "
                "while 2nd/right service `envelope_container` accepts that override, not using default.",
            ),
            (
                line_no(),
                "some_command diff % prod downstream rrr tt1 % tt1 % passive |",
                CompType.DescribeArgs,
                {
                    1: {
                        ServicePropName.run_mode.name: AssignedValue(
                            "active", ValueSource.default_value
                        ),
                    },
                    2: {
                        ServicePropName.run_mode.name: AssignedValue(
                            "active", ValueSource.default_value
                        ),
                    },
                    3: None,
                },
                {
                    1: {
                        ServicePropName.run_mode.name: [
                            "active",
                            "passive",
                        ],
                    },
                    2: {
                        ServicePropName.run_mode.name: [
                            "active",
                            "passive",
                        ],
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 1,
                    2: 2,
                },
                "Case A2: "
                "Similar to case A1, but now FS_97_64_39_94 `token_bucket` with override is not used by any of the "
                "two service `envelope_container`-s (both 1st/left and 2nd/right have no default overrides).",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    expected_container_ipos_to_used_token_bucket,
                    case_comment,
                ) = test_case
                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    None,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    None,
                    None,
                    expected_container_ipos_to_used_token_bucket,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_72_53_55_13_show_non_default_options_print_out_only(self):
        test_cases = [
            (
                line_no(),
                "some_command goto service dev downstream apac poiu-dd |",
                CompType.DescribeArgs,
                "FS_72_53_55_13: shows options hidden by default.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}downstream{TermColor.reset_style.value} {TermColor.consumed_token.value}apac{TermColor.reset_style.value} {TermColor.consumed_token.value}poiu-dd{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: ~ {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}code_maturity: dev {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}flow_stage: downstream {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}geo_region: apac {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-apac-downstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} hhh rrr 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}service_name: xx {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}host_name: poiu-dd {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.01 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.1.3 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_access_type.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}access_type: rw {TermColor.other_assigned_arg_value.value}[{ValueSource.default_value.name}]{TermColor.reset_style.value} {TermColor.caption_hidden_by_default.value}{ClientResponseHandlerDescribeLineArgs.default_overrides_caption}:{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}ro{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}rw{TermColor.reset_style.value} 
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto service dev downstream apac poiu-dd r|",
                CompType.DescribeArgs,
                "FS_72_53_55_13: shows `ro` option hidden by default and FS_11_87_76_73 highlights them by prefix.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}dev{TermColor.reset_style.value} {TermColor.consumed_token.value}downstream{TermColor.reset_style.value} {TermColor.consumed_token.value}apac{TermColor.reset_style.value} {TermColor.consumed_token.value}poiu-dd{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: ~ {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}code_maturity: dev {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}flow_stage: downstream {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}geo_region: apac {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: dev-apac-downstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} hhh {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}rr{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}service_name: xx {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}host_name: poiu-dd {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.01 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}ip_address: ip.192.168.1.3 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_access_type.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}access_type: {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}w{TermColor.reset_style.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.default_value.name}]{TermColor.reset_style.value} {TermColor.caption_hidden_by_default.value}{ClientResponseHandlerDescribeLineArgs.default_overrides_caption}:{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}o{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}r{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}w{TermColor.reset_style.value} 
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto service prod downstream rrr |",
                CompType.DescribeArgs,
                f"FS_72_53_55_13: non-default options with `{ClientResponseHandlerDescribeLineArgs.default_overrides_caption}` is only specified for {ValueSource.default_value}.",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}prod{TermColor.reset_style.value} {TermColor.consumed_token.value}downstream{TermColor.reset_style.value} {TermColor.consumed_token.value}rrr{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: ~ {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_n.value}3{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}code_maturity: prod {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}flow_stage: downstream {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}geo_region: apac {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: prod-apac-downstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}group_label: rrr {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*service_name: ?{TermColor.reset_style.value} tt1 tt2 xx 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.default_value.name}]{TermColor.reset_style.value} {TermColor.caption_hidden_by_default.value}overrides:{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}active{TermColor.reset_style.value} {TermColor.value_hidden_by_default.value}passive{TermColor.reset_style.value} 
{" " * indent_size}{TermColor.remaining_value.value}host_name: ?{TermColor.reset_style.value} wert-pd-1 wert-pd-2 
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.07 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}ip_address: ?{TermColor.reset_style.value} ip.192.168.7.3 ip.192.168.7.4 
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}{ReservedPropName.envelope_class.name}: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
""",
                # fmt: on
            ),
            (
                line_no(),
                "some_command goto service -ip ip.192.168.7.1 |",
                CompType.DescribeArgs,
                "FS_20_88_05_60: `dictated_arg` should be colored as `TermColor.explicit_offered_arg_value`",
                # fmt: off
                f"""
{TermColor.consumed_token.value}some_command{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.consumed_token.value}service{TermColor.reset_style.value} {TermColor.consumed_token.value}-ip{TermColor.reset_style.value} {TermColor.consumed_token.value}ip.192.168.7.1{TermColor.reset_style.value} 
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_1.value}1{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: some_command {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(2)}: service {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_state.name}: {FuncState.fs_demo.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.func_id.name}: {func_id_goto_service_} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_service.name}: {TermColor.found_count_n.value}2{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ServiceEnvelopeClass.class_service.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}code_maturity: prod {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}flow_stage: upstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}geo_region: apac {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}cluster_name: prod-apac-upstream {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*group_label: ?{TermColor.reset_style.value} aaa bbb sss 
{" " * indent_size}{TermColor.remaining_value.value}service_name: ?{TermColor.reset_style.value} s_a s_b 
{" " * indent_size}{TermColor.other_assigned_arg_value.value}run_mode: active {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}host_name: qwer-pd-1 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}live_status: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}data_center: dc.07 {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_dictated_arg_name_and_arg_value.value}ip_address: ip.192.168.7.1 {TermColor.explicit_dictated_arg_name_and_arg_value.value}[{ValueSource.explicit_dictated_arg.name}]{TermColor.reset_style.value}
{ServiceEnvelopeClass.class_access_type.name}: {TermColor.found_count_0.value}0{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}{ReservedPropName.envelope_class.name}: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
{" " * indent_size}{TermColor.no_option_to_suggest.value}access_type: {SpecialChar.NoPropValue.value}{TermColor.reset_style.value}
""",
                # fmt: on
            ),
        ]

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
            .set_test_data_ids_to_load(
                [
                    self.__class__.same_test_data_per_class,
                ]
            )
        )
        with outer_env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, ClientCommandLocal)
            interp_ctx = command_obj.interp_ctx

            if not stdout_str:
                # Output is not specified - not to be asserted:
                return

            # TODO: TODO_43_41_95_86: use server logger to disable stdout:
            #       Running print again with capturing `stdout`.
            #       Executing end-to-end above may generate
            #       noise output on `stdout`/`stderr` by local server logic.
            #       A proper implementation would probably be intercepting `DescribeArgs`'s response_dict
            #       and printing it separately (when no other logic with extra output can intervene)
            #       to assert the output.
            #       Alternatively, run this test via `ClientRemote` (see `RemoteTestClass`) where output
            #       of the server is not captured (as it is a separate process).
            inner_env_mock_builder = (
                EmptyEnvMockBuilder().set_capture_stdout(True).set_capture_stderr(True)
            )
            with inner_env_mock_builder.build():
                interp_result: InterpResult = InterpResult.from_interp_context(
                    interp_ctx
                )
                ClientResponseHandlerDescribeLineArgs.render_result(interp_result)

                self.assertEqual(
                    stdout_str,
                    inner_env_mock_builder.actual_stdout.getvalue(),
                )

                self.assertEqual(
                    "",
                    inner_env_mock_builder.actual_stderr.getvalue(),
                )
