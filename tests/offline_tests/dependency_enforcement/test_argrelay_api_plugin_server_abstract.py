from unittest import expectedFailure

import argrelay_api_plugin_server_abstract
import argrelay_app_server
import argrelay_test_infra
from argrelay_test_infra.test_infra import assert_test_module_name_embeds_prod_module_name
from offline_tests.dependency_enforcement.ForbiddenContractReportBuilder import ForbiddenContractReportBuilder
from offline_tests.dependency_enforcement.ImportLinterTestClass import ImportLinterTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(ImportLinterTestClass):

    def test_relationship(self):
        assert_test_module_name_embeds_prod_module_name(argrelay_api_plugin_server_abstract)

    # TODO: TODO_78_94_31_68: split argrelay into multiple packages:
    #       Populate rules for imports.

    def test_dependencies_between_rest_api_definitions_and_other_modules(self):
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs([
                f"{argrelay_api_plugin_server_abstract.__name__}.*",
            ])
            .add_forbidden_module_spec([
                f"{argrelay_test_infra.__name__}",
            ])
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
            .set_source_module_specs([
                f"{argrelay_api_plugin_server_abstract.__name__}.*",
            ])
            .add_forbidden_module_spec([
                f"{argrelay_app_server.__name__}",
            ])
            .build(),
        )
