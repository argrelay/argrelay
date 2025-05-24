from __future__ import annotations

from typing import Callable

from importlinter.adapters.building import GraphBuilder
from importlinter.adapters.printing import ClickPrinter
from importlinter.adapters.timing import SystemClockTimer
from importlinter.application.app_config import settings
from importlinter.application.ports.reporting import Report
from importlinter.application.rendering import (
    render_exception,
    render_report,
)
from importlinter.contracts.forbidden import ForbiddenContract
from importlinter.domain.contract import registry

from argrelay_lib_root.misc_helper_common import get_argrelay_dir
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass


# noinspection PyMethodMayBeStatic
class ImportLinterTestClass(BaseTestClass):
    """
    This base test class allows running `import-linter` as library for unit tests.

    See:
    https://github.com/seddonym/import-linter/issues/246
    """

    def run_import_linter(
        self,
        import_linter_reporter: Callable[[], Report],
    ) -> Report:
        """
        A helper which wraps each call to `import-linter` handling results and exceptions.
        """

        registry.register(ForbiddenContract, name="forbidden")

        settings.configure(
            GRAPH_BUILDER=GraphBuilder(),
            PRINTER=ClickPrinter(),
            TIMER=SystemClockTimer(),
            DEFAULT_CACHE_DIR=f"{get_argrelay_dir()}/tmp/import_linter_cache",
        )

        lint_report: Report | None = None
        try:
            lint_report = import_linter_reporter()
            render_report(lint_report)
        except Exception as e:
            render_exception(e)
            raise e

        if not lint_report:
            raise AssertionError(lint_report)
        if lint_report.contains_failures:
            raise AssertionError(lint_report)

    def assert_import_linter_success(
        self,
        import_linter_reporter: Callable[[], Report],
    ) -> Report:
        self.run_import_linter(
            import_linter_reporter,
        )

    def assert_import_linter_failure(
        self,
        failure_verifier: Callable[[Exception], None],
        import_linter_reporter: Callable[[], Report],
    ) -> Report:
        with self.assertRaises(Exception) as exc_context:
            self.run_import_linter(
                import_linter_reporter,
            )
        failure_verifier(exc_context)
