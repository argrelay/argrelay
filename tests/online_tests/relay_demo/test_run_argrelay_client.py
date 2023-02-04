import os
import subprocess
from unittest import TestCase, skipIf

from argrelay.test_helper import change_to_known_repo_path


class ThisTestCase(TestCase):

    @skipIf(
        not os.environ.get("ARGRELAY_DEV_SHELL", False),
        "Only `dev-shell.bash` controllably puts `relay_demo` in `PATH` env var - skip test otherwise.",
    )
    def test_invoke_via_shell(self):
        """
        Invokes client via generated `run_argrelay_client`.
        """

        with change_to_known_repo_path("."):
            # Function "desc_host" ("desc host") uses NoopInvocator, so the test should always pass
            subproc = subprocess.run(
                "relay_demo desc host dev upstream amer ro".split(" "),
            )
            ret_code = subproc.returncode
            if ret_code != 0:
                raise RuntimeError
