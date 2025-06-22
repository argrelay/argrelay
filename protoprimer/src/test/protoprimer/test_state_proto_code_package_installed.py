import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_client_dir_path_configured,
    Bootstrapper_state_py_exec_selected,
    EnvContext,
    EnvState,
    PythonExecutable,
)
from test_support import assert_test_module_name_embeds_enum_item_name


# noinspection PyPep8Naming
class ThisTestClass(PyfakefsTestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_enum_item_name(
            EnvState.state_proto_code_package_installed
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.install_editable_package",
    )
    def test_state_client_conf_file_path_exists(
        self,
        mock_install_editable_package,
        mock_state_py_exec_selected,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_configured.return_value = mock_client_dir

        self.fs.create_file(os.path.join(mock_client_dir, "src", "setup.py"))

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_proto_code_package_installed)

        # then:
        mock_install_editable_package.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                "src",
            )
        )
