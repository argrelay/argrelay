from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    func_envelope_path_step_prop_name,
)
from argrelay_lib_server_plugin_demo.demo_git.GitRepoEnvelopeClass import (
    GitRepoEnvelopeClass,
)
from argrelay_lib_server_plugin_demo.demo_git.GitRepoPropName import GitRepoPropName
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_26_43_73_72_func_tree(self):
        """
        Test `arg_value`-s suggestion with FS_26_43_73_72 func tree
        """

        test_cases = [
            (
                line_no(),
                "some_command desc tag |",
                CompType.DescribeArgs,
                [
                    "release",
                    "unstable",
                ],
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "desc",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "tag",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            GitRepoEnvelopeClass.class_git_tag.name,
                            ValueSource.init_value,
                        ),
                        GitRepoPropName.git_repo_alias.name: AssignedValue(
                            "argrelay", ValueSource.implicit_value
                        ),
                    },
                    3: None,
                },
                "Step 1: FS_44_36_84_88: both `tag` and `desc` are assigned `ValueSource.explicit_offered_arg` regardless of the order "
                "FS_26_43_73_72 interp tree: the ordered path to func `func_id_desc_git_tag` is `desc tag` ",
            ),
            (
                line_no(),
                "some_command tag desc |",
                CompType.DescribeArgs,
                [
                    "release",
                    "unstable",
                ],
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "desc",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "tag",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            GitRepoEnvelopeClass.class_git_tag.name,
                            ValueSource.init_value,
                        ),
                        GitRepoPropName.git_repo_alias.name: AssignedValue(
                            "argrelay", ValueSource.implicit_value
                        ),
                    },
                    3: None,
                },
                "Step 2: FS_44_36_84_88: both `tag` and `desc` are assigned `ValueSource.explicit_offered_arg` regardless of the order "
                "FS_26_43_73_72 interp tree: the ordered path to func `func_id_desc_git_tag` is `desc tag` ",
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
                    case_comment,
                ) = test_case

                self.verify_output_with_new_server_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                )
