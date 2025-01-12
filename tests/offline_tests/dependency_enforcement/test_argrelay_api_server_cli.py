from argrelay_api_server_cli import schema_request, schema_response
from argrelay_api_server_cli.server_spec import DescribeLineArgsSpec, ProposeArgValuesSpec, RelayLineArgsSpec
from offline_tests.dependency_enforcement.ForbiddenContractReportBuilder import ForbiddenContractReportBuilder
from offline_tests.dependency_enforcement.ImportLinterTestClass import ImportLinterTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(ImportLinterTestClass):

    # TODO: TODO_78_94_31_68: split argrelay into multiple packages:
    #       Populate rules for imports.

    def test_dependencies_between_rest_api_definitions_and_other_modules(self):
        """
        REST API specs are not used by any other module under `argrelay_api_server_cli`.
        """
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs([
                f"{schema_request.__name__}.*",
                f"{schema_response.__name__}.*",
            ])
            .add_forbidden_module_spec([
                f"{DescribeLineArgsSpec.__name__}",
                f"{ProposeArgValuesSpec.__name__}",
                f"{RelayLineArgsSpec.__name__}",
            ])
            .build(),
        )
