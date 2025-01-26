import argrelay_api_server_cli
from argrelay_api_server_cli import (
    schema_request,
    schema_response,
)
from argrelay_api_server_cli.server_spec import (
    DescribeLineArgsSpec,
    ProposeArgValuesSpec,
    RelayLineArgsSpec,
)
from offline_tests.dependency_enforcement.ForbiddenContractReportBuilder import ForbiddenContractReportBuilder
from offline_tests.dependency_enforcement.ImportLinterTestClass import ImportLinterTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(ImportLinterTestClass):
    """
    Verify assumptions about how `import-linter` works.
    """

    def test_import_linter_succeeds(self):
        """
        Test that `import-linter` succeeds when it should.
        """
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_title(
                f"{True}: REST API specs are not used by anything in `{argrelay_api_server_cli.__name__}`."
            )
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

    def test_import_linter_fails(self):
        """
        Test that `import-linter` fails when it should.
        """
        self.assert_import_linter_failure(
            lambda exc_context: self.assertEqual(
                AssertionError,
                type(exc_context.exception),
            ),
            lambda: ForbiddenContractReportBuilder()
            .set_title(
                f"{False}: `{DescribeLineArgsSpec.__name__}` does not depend on `{schema_request.__name__}`."
            )
            .set_source_module_specs([
                f"{DescribeLineArgsSpec.__name__}",
            ])
            .add_forbidden_module_spec([
                f"{schema_request.__name__}.*",
            ])
            .build(),
        )
