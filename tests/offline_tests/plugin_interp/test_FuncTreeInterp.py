from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no

from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_26_43_73_72_func_tree(self):
        """
        Test arg values suggestion with FS_26_43_73_72 func tree
        """

        test_cases = [
            (
                line_no(),
                "some_command desc tag |",
                CompType.DescribeArgs,
                [],
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("desc", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("tag", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            GitRepoEnvelopeClass.ClassGitTag.name,
                            ArgSource.InitValue,
                        ),
                        GitRepoArgType.git_repo_alias.name: AssignedValue("argrelay", ArgSource.ImplicitValue),
                    },
                    3: None,
                },
                "Step 1: FS_44_36_84_88: both `tag` and `desc` are assigned `ArgSource.ExplicitPosArg` regardless of the order "
                "FS_26_43_73_72 interp tree: the ordered path to func `desc_git_tag_func` is `desc tag` ",
            ),
            (
                line_no(),
                "some_command tag desc |",
                CompType.DescribeArgs,
                [],
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("desc", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("tag", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            GitRepoEnvelopeClass.ClassGitTag.name,
                            ArgSource.InitValue,
                        ),
                        GitRepoArgType.git_repo_alias.name: AssignedValue("argrelay", ArgSource.ImplicitValue),
                    },
                    3: None,
                },
                "Step 2: FS_44_36_84_88: both `tag` and `desc` are assigned `ArgSource.ExplicitPosArg` regardless of the order "
                "FS_26_43_73_72 interp tree: the ordered path to func `desc_git_tag_func` is `desc tag` ",
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
