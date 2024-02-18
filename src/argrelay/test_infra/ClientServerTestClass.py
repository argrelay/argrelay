import signal
import socket
import subprocess
import time
from contextlib import closing
from datetime import datetime, timedelta

from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.test_infra import change_to_known_repo_path
from argrelay.test_infra.InOutTestClass import InOutTestClass


class ClientServerTestClass(InOutTestClass):
    """
    Unlike tests derived from `ManualServerTestClass` (which rely on the server to be started manually),
    the test controls startup of the server.

    This test starts server (only) via their generated files in `@/bin/` dir.

    Avoiding generated file in `@/bin/` dir for client
    allows executing client code within the OS process responsible for running this test.
    In turn, this allows using `EnvMockBuilder` for client-side mocking to
    intercept server responses (see `RemoteTestClass`).
    """

    server_proc = None

    @classmethod
    def setUpClass(cls):
        InOutTestClass.setUpClass()
        cls.start_server()

    @classmethod
    def tearDownClass(cls):
        InOutTestClass.setUpClass()
        cls.stop_server()

    @classmethod
    def start_server(cls):
        with change_to_known_repo_path("."):
            cls.server_proc = subprocess.Popen([
                f"{get_argrelay_dir()}/exe/run_argrelay_server",
            ])
        cls.wait_for_connection_to_server()

    @classmethod
    def stop_server(cls):
        # shutdown gracefully:
        cls.server_proc.send_signal(signal.SIGINT)
        cls.server_proc.communicate()
        cls().assertEqual(0, cls.server_proc.returncode)

    @staticmethod
    def wait_for_connection_to_server():
        client_config: ClientConfig = client_config_desc.obj_from_default_file()

        delay_s = 1
        # 10 mins should be enough, right?
        timeout_ts = datetime.now() + timedelta(minutes = 10.0)
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
                    now_ts = datetime.now()
                    if now_ts > timeout_ts:
                        raise TimeoutError
                    print(
                        f"now: {now_ts.time()} timeout: {timeout_ts.time()} - waiting {delay_s} sec for connection to server..."
                    )
                    time.sleep(delay_s)
                    delay_s += 1 if delay_s < 30 else 0
                    continue
