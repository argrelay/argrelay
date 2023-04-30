import os
import subprocess
from unittest import TestCase, skipIf

from argrelay.test_helper import change_to_known_repo_path


class ThisTestCase(TestCase):

    @skipIf(
        not os.environ.get("ARGRELAY_DEV_SHELL", False),
        """
        Only `^/exe/dev_shell.bash` controllably puts `${ARGRELAY_CLIENT_COMMAND}`into `PATH` env var.
        Skip test otherwise.
        """,
    )
    def test_invoke_via_shell(self):
        """
        Invokes client via generated `^/bin/run_argrelay_client`.
        """

        with change_to_known_repo_path("."):
            client_command_env_var_name = "ARGRELAY_CLIENT_COMMAND"
            # Function "desc_host" ("desc host") uses NoopDelegator, so the test should always pass
            subproc = subprocess.run(
                f"{os.environ.get(client_command_env_var_name)} desc host dev upstream amer ro".split(" "),
            )
            ret_code = subproc.returncode
            if ret_code != 0:
                raise RuntimeError
