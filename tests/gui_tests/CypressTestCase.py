from __future__ import annotations

import subprocess

from argrelay.test_helper import change_to_known_repo_path
from argrelay.test_helper.ClientServerTestCase import ClientServerTestCase


class CypressTestCase(ClientServerTestCase):
    """
    Base class to run GUI tests via Cypress.

    See `gui_tests_notes.md` how to run this manually.
    """

    @classmethod
    def run_cypress_test_scripts_in_paths(
        cls,
        paths_spec,
    ):
        with change_to_known_repo_path("./tests/gui_tests"):
            sub_proc = subprocess.run(
                [
                    "npx",
                    "cypress",
                    "run",
                    "--spec",
                    paths_spec,
                ],
            )
            exit_code = sub_proc.returncode
            if exit_code != 0:
                raise RuntimeError

    @classmethod
    def run_cypress_test_script(
        cls,
        script_name
    ):
        cls.run_cypress_test_scripts_in_paths(
            f"cypress/e2e/argrelay_gui/{script_name}",
        )
