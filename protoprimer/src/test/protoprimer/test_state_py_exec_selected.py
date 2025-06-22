import os
import sys
import unittest
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_env_conf_file_data,
    Bootstrapper_state_env_conf_file_path,
    Bootstrapper_state_client_dir_path_specified,
    Bootstrapper_state_py_exec_specified,
    ArgConst,
    Bootstrapper_state_script_dir_path,
    Bootstrapper_state_target_dst_dir_path,
    ConfConstEnv,
    ConfConstGeneral,
    EnvContext,
    EnvState,
    PythonExecutable,
)
from test_support import assert_test_module_name_embeds_enum_item_name

mock_client_dir = "/mock_client_dir"
script_dir = os.path.dirname(os.path.abspath(__file__))
target_dst_dir_path = "target_dst_dir"

non_default_file_abs_path_python = "/oct/bin/python3"
non_default_dir_abs_path_venv = "/another/venv"


# noinspection PyPep8Naming
class ThisTestClass(PyfakefsTestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        self.fs.create_dir(script_dir)

        self.fs.create_dir(target_dst_dir_path)

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_enum_item_name(EnvState.state_py_exec_selected)

    def test_assumptions_used_in_other_tests(self):
        self.assertNotEqual(
            non_default_file_abs_path_python,
            ConfConstEnv.default_file_abs_path_python,
        )

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_on_path_to_curr_python_is_outside_of_path_to_venv_when_venv_is_created(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir
        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        mock_venv_create.assert_called_once_with(
            os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
            ),
            with_pip=True,
        )
        path_to_python = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_python,
            [
                path_to_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_failure_when_path_to_python_is_inside_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_env_conf_file_path,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_path.return_value = (
            "fake: " + EnvState.state_env_conf_file_path.name
        )

        mock_state_env_conf_file_data.return_value = {
            # NOTE: `python` path is inside `venv`:
            ConfConstEnv.field_file_abs_path_python: os.path.join(
                mock_client_dir,
                ConfConstEnv.default_dir_rel_path_venv,
                ConfConstGeneral.file_rel_path_venv_python,
            ),
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        self.assertIn(
            f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance.",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_not_called()

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/mock_client_dir/venv/wrong/path/to/python",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_failure_when_path_to_curr_python_is_inside_venv_but_different_from_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        self.assertIn(
            f"it does not match expected interpreter",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_matches_interpreter_and_venv_does_not_exist(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: ConfConstEnv.default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        path_to_venv = os.path.join(
            mock_client_dir,
            ConfConstEnv.default_dir_rel_path_venv,
        )
        mock_venv_create.assert_called_once_with(
            path_to_venv,
            with_pip=True,
        )
        path_to_python = os.path.join(
            path_to_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_python,
            [
                path_to_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value=ConfConstEnv.default_file_abs_path_python,
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_differs_from_path_to_curr_python_and_execv_called(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_initial

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: non_default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: ConfConstEnv.default_dir_rel_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        mock_venv_create.assert_not_called()
        mock_execv.assert_called_once_with(
            non_default_file_abs_path_python,
            [
                non_default_file_abs_path_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_required.name,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_target_dst_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_py_exec_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_specified.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_file_data.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value=non_default_file_abs_path_python,
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
        mock_state_env_conf_file_data,
        mock_state_client_dir_path_specified,
        mock_state_py_exec_specified,
        mock_state_script_dir_path,
        mock_state_target_dst_dir_path,
    ):
        # given:

        mock_state_target_dst_dir_path.return_value = target_dst_dir_path

        mock_state_script_dir_path.return_value = script_dir

        mock_state_py_exec_specified.return_value = PythonExecutable.py_exec_required

        mock_state_client_dir_path_specified.return_value = mock_client_dir

        mock_state_env_conf_file_data.return_value = {
            ConfConstEnv.field_file_abs_path_python: non_default_file_abs_path_python,
            ConfConstEnv.field_dir_rel_path_venv: non_default_dir_abs_path_venv,
        }

        # when:

        self.env_ctx.bootstrap_state(EnvState.state_py_exec_selected)

        # then:

        mock_venv_create.is_not_called()

        mock_venv_create.assert_called_once_with(
            non_default_dir_abs_path_venv,
            with_pip=True,
        )

        path_to_python = os.path.join(
            non_default_dir_abs_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        mock_execv.assert_called_once_with(
            path_to_python,
            [
                path_to_python,
                *sys.argv,
                ArgConst.arg_py_exec,
                PythonExecutable.py_exec_venv.name,
            ],
        )

        mock_get_path_to_curr_python.assert_called_once()

    ####################################################################################################################
