from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_delegator.DelegatorNoopNoDataFunc import DelegatorNoopNoDataFunc
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no, assert_test_module_name_embeds_prod_class_name
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorNoopNoDataFunc)

    def test_func_id_no_data(self):
        """
        Test `SpecialFunc.func_id_no_data`.
        """

        test_cases = [
            (
                line_no(),
                "some_command no_data |",
                CompType.PrefixShown,
                [
                ],
                None,
                None,
                "Func `no_data` suggests nothing.",
            ),
            (
                line_no(),
                "some_command no_data |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "no_data",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                    },
                    2: None,
                },
                None,
                "Func `no_data` gets no assigned values.",
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
                    case_comment,
                ) = test_case

                self.verify_output_with_new_server_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    None,
                )
