from unittest import expectedFailure

import argrelay_api_server_cli
import argrelay_app_bootstrap
import argrelay_app_check_env
import argrelay_app_client
import argrelay_app_server
import argrelay_test_infra
from argrelay_api_server_cli import (
    schema_request,
    schema_response,
)
from argrelay_api_server_cli.server_spec import (
    DescribeLineArgsSpec,
    ProposeArgValuesSpec,
    RelayLineArgsSpec,
)
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
        assert_test_module_name_embeds_prod_module_name(argrelay_api_server_cli)

    # TODO: TODO_78_94_31_68: split argrelay into multiple packages:
    #       Populate rules for imports.

    def test_dependencies_between_rest_api_definitions_and_other_modules(self):
        """
        REST API specs are not used by any other module under `argrelay_api_server_cli`.
        """
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs(
                [
                    f"{argrelay_api_server_cli.__name__}.*",
                ]
            )
            .add_forbidden_module_spec(
                [
                    f"{argrelay_app_bootstrap.__name__}",
                    f"{argrelay_app_check_env.__name__}",
                    f"{argrelay_app_client.__name__}",
                ]
            )
            .build(),
        )

    def test_rest_api(self):
        """
        REST API specs are not used by any other module under `argrelay_api_server_cli`.
        """
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs(
                [
                    f"{schema_request.__name__}.*",
                    f"{schema_response.__name__}.*",
                ]
            )
            .add_forbidden_module_spec(
                [
                    f"{DescribeLineArgsSpec.__name__}",
                    f"{ProposeArgValuesSpec.__name__}",
                    f"{RelayLineArgsSpec.__name__}",
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
    def test_expected_wrong_dependencies_2(self):
        self.assert_import_linter_success(
            lambda: ForbiddenContractReportBuilder()
            .set_source_module_specs(
                [
                    f"{argrelay_api_server_cli.__name__}.*",
                ]
            )
            .add_forbidden_module_spec(
                [
                    f"{argrelay_app_server.__name__}",
                ]
            )
            .build(),
        )
