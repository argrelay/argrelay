import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

import protoprimer
from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_client_dir_path_configured,
    Bootstrapper_state_py_exec_selected,
    Bootstrapper_state_script_dir_path,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    PythonExecutable,
    read_text_file,
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
            EnvState.state_proto_code_copy_updated
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
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
        mock_state_script_dir_path,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        script_dir = os.path.join(
            mock_client_dir,
            "cmd",
        )
        script_path = os.path.join(
            script_dir,
            # TODO: be able to configure it:
            ConfConstGeneral.default_proto_copy_basename,
        )
        # script copy:
        self.fs.create_file(
            script_path,
        )
        # script orig (in fake filesystem):
        self.fs.create_file(
            protoprimer.proto_code.__file__,
            # Not real code, just 1000 empty lines:
            contents="\n" * 1000,
        )
        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_configured.return_value = mock_client_dir

        self.fs.create_file(os.path.join(mock_client_dir, "src", "setup.py"))

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_proto_code_copy_updated)

        # then:
        mock_install_editable_package.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                "src",
            )
        )
        script_obj = self.fs.get_object(script_path)
        self.assertIn(
            ConfConstGeneral.func_get_script_copy_generated_boilerplate(
                protoprimer.proto_code
            ),
            script_obj.contents,
        )
