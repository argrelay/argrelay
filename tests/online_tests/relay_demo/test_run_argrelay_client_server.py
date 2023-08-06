import os
import signal
import socket
import subprocess
import time
from contextlib import closing
from unittest import TestCase, skipIf

from argrelay.misc_helper import get_argrelay_dir
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.test_helper import change_to_known_repo_path


@skipIf(
    (
        (not os.environ.get("ARGRELAY_DEV_SHELL", False))
        or
        (not os.environ.get("ARGRELAY_BOOTSTRAP_DEV_ENV", False))
    ),
    """
    Only `@/exe/dev_shell.bash` controllably puts `${ARGRELAY_CLIENT_COMMAND}` into `PATH` env var.
    Skip test otherwise.
    """,
)
class ThisTestCase(TestCase):
    """
    It tests both client and server started via their generated files in `@/bin/` dir.

    The test starts background server process to execute the client.
    """

    server_proc = None

    def setUp(self):
        # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
        self.server_proc = subprocess.Popen([
            f"{get_argrelay_dir()}/bin/run_argrelay_server",
        ])
        self.wait_for_connection_to_server()

    def tearDown(self):
        # shutdown gracefully:
        self.server_proc.send_signal(signal.SIGINT)
        self.server_proc.communicate()
        self.assertEquals(0, self.server_proc.returncode)

    def test_invoke_via_shell(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client`.
        """

        with change_to_known_repo_path("."):
            client_command_env_var_name = "ARGRELAY_CLIENT_COMMAND"
            # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
            client_proc = subprocess.run(
                f"{os.environ.get(client_command_env_var_name)} desc host dev upstream amer ro".split(" "),
            )
            ret_code = client_proc.returncode
            if ret_code != 0:
                raise RuntimeError

    @staticmethod
    def wait_for_connection_to_server():
        client_config: ClientConfig = client_config_desc.from_default_file()

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            while True:
                result = sock.connect_ex((
                    client_config.connection_config.server_host_name,
                    client_config.connection_config.server_port_number,
                ))
                if result == 0:
                    print("connected to server")
                    return
                else:
                    print("waiting for connection to server")
                    time.sleep(1)
                    continue
