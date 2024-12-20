from argrelay.enum_desc.CompType import CompType
from argrelay.plugin_delegator.DelegatorError import DelegatorError
from argrelay.plugin_interp.FuncTreeInterpFactory import tree_step_prop_name_prefix_
from argrelay.test_infra import line_no, assert_test_func_name_embeds_prod_class_name
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_every_CompType_FS_20_88_05_60_dictated_arg(self):
        """
        Test `arg_value`-s suggestion with FS_20_88_05_60 `dictated_arg`-s and TD_63_37_05_36 demo data
        """

        assert_test_func_name_embeds_prod_class_name(CompType)

        test_cases = [
            (
                line_no(), "some_command -|", comp_type,
                [
                    "-envelope_class",
                    "-func_id",
                    "-func_state",
                    f"-{tree_step_prop_name_prefix_}0",
                    f"-{tree_step_prop_name_prefix_}1",
                    f"-{tree_step_prop_name_prefix_}2",
                    f"-{tree_step_prop_name_prefix_}3",
                ],
                # Only `CompType.InvokeAction` fails (because function is not selected):
                DelegatorError if comp_type == CompType.InvokeAction else None,
                "FS_20_88_05_60 dictated_args: suggest list of `dictated_arg`-s for func search",
            ) for comp_type in CompType
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
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    delegator_class,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
