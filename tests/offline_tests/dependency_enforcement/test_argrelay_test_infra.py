import argrelay_test_infra
from offline_tests.dependency_enforcement.ForbiddenContractReportBuilder import ForbiddenContractReportBuilder
from offline_tests.dependency_enforcement.ImportLinterTestClass import ImportLinterTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(ImportLinterTestClass):

    def test_dependencies_between_rest_api_definitions_and_other_modules(self):
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs([
                f"{argrelay_test_infra.__name__}.*",
            ])
            .add_forbidden_module_spec([
            ])
            .build(),
        )
