from unittest import expectedFailure

import argrelay
import argrelay_api_server_cli
import argrelay_app_check_env
import argrelay_lib_root
import argrelay_test_infra
from argrelay_test_infra.test_infra import (
    assert_test_module_name_embeds_prod_module_name,
)
from offline_tests.dependency_enforcement.ForbiddenContractReportBuilder import (
    ForbiddenContractReportBuilder,
)
from offline_tests.dependency_enforcement.ImportLinterTestClass import (
    ImportLinterTestClass,
)


# noinspection PyMethodMayBeStatic
class ThisTestClass(ImportLinterTestClass):

    def test_relationship(self):
        assert_test_module_name_embeds_prod_module_name(argrelay_lib_root)

    # TODO: TODO_78_94_31_68: split argrelay into multiple packages:
    #       Eventually, `argrelay_lib_root` may even need to be removed.

    def test_dependencies_between_rest_api_definitions_and_other_modules(self):
        """
        Module `argrelay_lib_root` should not depend on any other modules.
        """
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs(
                [
                    f"{argrelay_lib_root.__name__}.*",
                ]
            )
            .add_forbidden_module_spec(
                [
                    f"{argrelay.__name__}.*",
                    f"{argrelay_app_check_env.__name__}",
                    f"{argrelay_test_infra.__name__}",
                ]
            )
            .build(),
        )

    # TODO: TODO_78_94_31_68: split argrelay into multiple packages:
    #       This test should not fail.
    #       When dependencies fixed, move this to:
    #       `test_dependencies_between_rest_api_definitions_and_other_modules`.
    @expectedFailure
    def test_expected_wrong_dependencies_1(self):
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs(
                [
                    f"{argrelay_lib_root.__name__}.*",
                ]
            )
            .add_forbidden_module_spec(
                [
                    f"{argrelay_api_server_cli.__name__}",
                ]
            )
            .build(),
        )
