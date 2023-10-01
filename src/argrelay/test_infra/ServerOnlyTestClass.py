from argrelay.relay_server.CustomFlaskApp import CustomFlaskApp
from argrelay.relay_server.__main__ import create_app
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ServerOnlyTestClass(BaseTestClass):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #7.

    Server-only test without running `argrelay` client at all.

    Note:
    This option is only suitable to run test via `FlaskApp.test_client()`.
    It is not suitable to start server with ports exposed to external clients (e.g. to test GUI).
    To make `FlaskApp` open ports, it requires ugly double-thread-wrapping:
    https://stackoverflow.com/a/56860638/441652
    However, even if it is done to open ports, there is next big problem - there is no known way close the ports.
    There is no known way to control `FlaskApp` instance once it starts (to re-spawn).
    Even shutting down server by throwing exception does not work as the server instance still holds the ports
    open within current test process - new server instance within current test process cannot be re-spawn:
    https://stackoverflow.com/a/42699779/441652
    Exiting current test process prevents all subsequent tests from running - this is not an option either.
    Again, this test class is limited to tests via `FlaskApp.test_client()`.
    To run GUI against the server, use FS_66_17_43_42 test_infra / special test mode #5 instead.
    """

    flask_app: CustomFlaskApp

    @classmethod
    def create_server_in_mocked_env(
        cls,
        env_mock_builder: ServerOnlyEnvMockBuilder,
    ):
        """
        Creates `CustomFlaskApp` started in mocked environment.

        Use case: access FlaskApp.test_client.
        """

        with env_mock_builder.build():
            # This block mocks access to configs while starting Flask.
            # The `env_mock_builder` is ineffective during run of the test cases
            # because this block will already be over.
            # However, the Flask server will still be running for all test cases
            # with the state affected by the mock config data given here.

            cls.flask_app = create_app()

            # Making sure Flask read the mocked server config:
            env_mock_builder.assert_server_config_read()
