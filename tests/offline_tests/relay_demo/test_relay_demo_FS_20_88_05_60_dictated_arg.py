from argrelay.custom_integ.DelegatorServiceInstanceGoto import DelegatorServiceInstanceGoto
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_delegator.DelegatorError import DelegatorError
from argrelay.plugin_interp.FuncTreeInterpFactory import (
    tree_step_prop_name_prefix_, func_envelope_path_step_prop_name,
    tree_step_arg_name_prefix_,
)
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no, assert_test_func_name_embeds_prod_class_name
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass

class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # TODO: TODO_66_09_41_16: clarify command line processing:
    # TODO: Test scenarios for FS_20_88_05_60 `dictated_arg`:
    #
    #       *  TODO: Do not eat `dictated_arg` if it does not match `prop_name`.
    #
    #       *  TODO: `token_bucket` and `dictated_arg`:
    #                 Ensure suggestions for current `envelope_container` happen only
    #                 if `dictated_arg` is in the same `token_bucket`.
    #
    #       *  TODO: `offered_arg` and `dictated_arg`: if `dictated_arg` is eaten, `offered_arg` cannot be eaten for the same `prop_name`.
    #
    #       *  TODO: `tangent_token` and `dictated_arg`: ensure `tangent_token` does not force-assign value
    #                test this on different `CompType`-s
    #
    #       *  TODO: incomplete `dictated_arg`: ensure incomplete `arg_value` is not used as value in search.
    #                test this on different `CompType`-s
    #
    #       *  TODO: Suggest:
    #          *     only remaining `prop_name`-s of current `envelope_container` on `CompScope.ScopeInitial` or `CompScope.ScopeUnknown`
    #          *     all `prop_name`-s of current `envelope_container` on `CompScope.ScopeSubsequent`
    #
    #       *  TODO: ensure that `dictated_arg` overrides defaults.
    #
    #       *  TODO: Ensure that explicit `dictated_arg` is printed in the correct
    #                color for explicit parameters in `enum` func ("describe")

    def test_every_CompType_FS_20_88_05_60_dictated_arg(self):
        """
        Test `arg_value`-s suggestion with FS_20_88_05_60 `dictated_arg`-s and TD_63_37_05_36 demo data
        """

        assert_test_func_name_embeds_prod_class_name(CompType)

        test_cases = [
            (
                line_no(), "some_command -|", comp_type,
                [
                    "-id",
                    "-state",
                    f"-{tree_step_arg_name_prefix_}1",
                    f"-{tree_step_arg_name_prefix_}2",
                    f"-{tree_step_arg_name_prefix_}3",
                ],
                # Only `CompType.InvokeAction` fails (because function is not selected):
                DelegatorError if comp_type == CompType.InvokeAction else None,
                "FS_20_88_05_60 CASE_A: dictated_args: suggest (remaining) list of `dictated_arg`-s for func search",
            ) for comp_type in CompType if comp_type not in [
                # `SubsequentHelp` list full list of `arg_name`-s:
                CompType.SubsequentHelp
            ]
        ] + [
            (
                line_no(), "some_command -|", CompType.SubsequentHelp,
                [
                    "-class",
                    "-id",
                    "-state",
                    f"-{tree_step_arg_name_prefix_}0",
                    f"-{tree_step_arg_name_prefix_}1",
                    f"-{tree_step_arg_name_prefix_}2",
                    f"-{tree_step_arg_name_prefix_}3",
                ],
                None,
                "FS_20_88_05_60 CASE_B: dictated_args: suggest (full) list of `dictated_arg`-s for func search",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    delegator_class,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    test_data = self.__class__.same_test_data_per_class,
                    test_line = test_line,
                    comp_type = comp_type,
                    expected_suggestions = expected_suggestions,
                    container_ipos_to_expected_assignments = None,
                    container_ipos_to_options_hidden_by_default_value = None,
                    delegator_class = delegator_class,
                    envelope_ipos_to_prop_values = None,
                    expected_container_ipos_to_used_token_bucket = None,
                    init_env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_consumption_and_suggestion_of_dictated_args(self):
        """
        Consumption of FS_20_88_05_60 `dictated_arg`-s
        """

        test_cases = [
            (
                line_no(),
                "some_command goto service -ip ip.172.16.1.2 |",
                CompType.InvokeAction,
                [
                ],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
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
                        ServicePropName.ip_address.name: AssignedValue(
                            "ip.172.16.1.2",
                            ValueSource.explicit_dictated_arg,
                        ),
                    },
                    2: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_access_type.name,
                            ValueSource.init_value,
                        ),
                    },
                    3: None,
                },
                # As of now, `DelegatorServiceInstanceGoto` redirects all
                # invocations to `DelegatorError` unconditionally:
                DelegatorServiceInstanceGoto if False else DelegatorError,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "tt",
                        ServicePropName.host_name.name: "zxcv-dd",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_access_type.name,
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: 0,
                    3: 0,
                },
                "CASE_A: (with empty tangent token) Consume FS_20_88_05_60 `dictated_arg` with `arg_name` `ip` and `arg_value` `ip.172.16.1.2` - "
                "this singles out service (there is only one for that `ip`)."
            ),
            (
                line_no(),
                "some_command goto service -ip ip.172.16.1.2|",
                CompType.InvokeAction,
                [

                ],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
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
                        ServicePropName.ip_address.name: AssignedValue(
                            "ip.172.16.1.2",
                            ValueSource.explicit_dictated_arg,
                        ),
                    },
                    2: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_access_type.name,
                            ValueSource.init_value,
                        ),
                    },
                    3: None,
                },
                    # As of now, `DelegatorServiceInstanceGoto` redirects all
                    # invocations to `DelegatorError` unconditionally:
                DelegatorServiceInstanceGoto if False else DelegatorError,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "tt",
                        ServicePropName.host_name.name: "zxcv-dd",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_access_type.name,
                    },
                    3: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: 0,
                    3: 0,
                },
                "CASE_B: (with non-empty tangent token) Consume FS_20_88_05_60 `dictated_arg` with `arg_name` `ip` and `arg_value` `ip.172.16.1.2` - "
                "this singles out service (there is only one for that `ip`)."
            ),
            (
                line_no(),
                "some_command goto service -ip |",
                CompType.InvokeAction,
                [
                    "ip.172.16.1.2 # zxcv-dd",
                    "ip.172.16.2.1 # asdf-du",
                    "ip.172.16.4.2 # poiu-qu",
                    "ip.172.16.7.2 # qwer-pd-2",
                    "ip.192.168.1.1 # zxcv-du",
                    "ip.192.168.1.3 # poiu-dd",
                    "ip.192.168.2.2 # xcvb-dd",
                    "ip.192.168.3.1 # qwer-du",
                    "ip.192.168.4.1 # hjkl-qu",
                    "ip.192.168.6.1 # rtyu-qu",
                    "ip.192.168.6.3 # sdfgh-qd",
                    "ip.192.168.6.4 # sdfgb-qd",
                    "ip.192.168.7.1 # qwer-pd-1",
                    "ip.192.168.7.2 # qwer-pd-3",
                    "ip.192.168.7.3 # wert-pd-1",
                    "ip.192.168.7.4 # wert-pd-2",
                ],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
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
                    },
                    2: {
                    },
                    3: None,
                },
                # As of now, `DelegatorServiceInstanceGoto` redirects all
                # invocations to `DelegatorError` unconditionally:
                DelegatorServiceInstanceGoto if False else DelegatorError,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                    },
                    # Many other `data_envelope`-s with `ServiceEnvelopeClass.class_service`:
                    # ...
                    26: None,
                },
                {
                    0: 0,
                    1: 0,
                    2: None,
                },
                "(with empty tangent token) Propose for (incomplete) FS_20_88_05_60 `dictated_arg` with "
                "`arg_name` `ip` and missing `arg_value` - "
                "this should propose all known `ip_address`-es."
            ),
            (
                line_no(),
                "lay goto service -dc dc.04 |",
                CompType.InvokeAction,
                [
                    "aaa",
                    "bbb",
                    "sss",
                ],
                None,
                # As of now, `DelegatorServiceInstanceGoto` redirects all
                # invocations to `DelegatorError` unconditionally:
                DelegatorServiceInstanceGoto if False else DelegatorError,
                None,
                None,
                "(with empty tangent token) Propose for `prop_value`-s from next remaining `prop_name`."
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    case_comment,
                ) = test_case

                self.skip_test_when_line_is_not_expected(
                    line_number,
                    None,
                )

                self.verify_output_via_local_client(
                    test_data = self.__class__.same_test_data_per_class,
                    test_line = test_line,
                    comp_type = comp_type,
                    expected_suggestions = expected_suggestions,
                    container_ipos_to_expected_assignments = container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value = None,
                    delegator_class = delegator_class,
                    envelope_ipos_to_prop_values = envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket = expected_container_ipos_to_used_token_bucket,
                    init_env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
