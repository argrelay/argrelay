import signal
import socket
import subprocess
import time
from contextlib import closing

from argrelay.misc_helper import get_argrelay_dir
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.test_helper import change_to_known_repo_path
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ClientServerTestCase(InOutTestCase):
    """
    Unlike tests derived from `ManualServerTest` (which rely on the server to be started manually),
    the test controls startup of the server.

    This test starts server (only) via their generated files in `@/bin/` dir.

    Avoiding generated file in `@/bin/` dir for client
    allows executing client code within the OS process responsible for running this test.
    In turn, this allows using `EnvMockBuilder` for client-side mocking to
    intercept server responses (see `RemoteTestCase`).
    """

    server_proc = None

    @classmethod
    def setUpClass(cls):
        InOutTestCase.setUpClass()
        with change_to_known_repo_path("."):
            cls.server_proc = subprocess.Popen([
                f"{get_argrelay_dir()}/bin/run_argrelay_server",
            ])
        cls.wait_for_connection_to_server()

    @classmethod
    def tearDownClass(cls):
        InOutTestCase.setUpClass()
        # shutdown gracefully:
        cls.server_proc.send_signal(signal.SIGINT)
        cls.server_proc.communicate()
        cls().assertEqual(0, cls.server_proc.returncode)

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
