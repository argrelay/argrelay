import os
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript import proto_code
from protoscript.proto_code import (
    EnvContext,
)


# noinspection PyPep8Naming
class ThisTestClass_recurse_with_required_python_interpreter(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `recurse_with_required_python_interpreter`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_writing_path_to_python_when_missing_and_path_to_curr_python_is_outside_of_path_to_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        state_proj_dir_path_configured = mock_proj_dir
        value_path_to_python = os.path.join(
            state_proj_dir_path_configured,
            value_path_to_python,
        )
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        path_to_python_path = "/mock_proj_dir/conf/python_env.path_to_python.conf.txt"

        # when:
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        path_to_python_value = read_line_file(path_to_python_path)
        self.assertEqual(path_to_python_value, "/usr/bin/python3")
        mock_venv_create.assert_called_once_with(
            "/mock_proj_dir/venv",
            with_pip=True,
        )
        mock_execv.assert_called_once_with(
            "/mock_proj_dir/venv/bin/python",
            [
                "/mock_proj_dir/venv/bin/python",
                *sys.argv,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_failure_when_path_to_python_is_inside_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_python.conf.txt",
            contents="venv/bin/python\n",
        )

        # when
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            with self.assertRaises(AssertionError) as cm:
                self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance.",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/mock_proj_dir/venv/bin/python",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_failure_when_path_to_curr_python_is_inside_venv_but_path_to_python_is_still_missing(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )

        # when
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            with self.assertRaises(AssertionError) as cm:
                self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"still does not exists",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/mock_proj_dir/venv/wrong/path/to/python",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_failure_when_path_to_curr_python_is_inside_venv_but_different_from_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )

        # when
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            with self.assertRaises(AssertionError) as cm:
                self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"it does not match expected interpreter",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_matches_interpreter_and_venv_does_not_exist(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_python.conf.txt",
            contents="/usr/bin/python3\n",
        )

        # when:
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.assert_called_once_with(
            "/mock_proj_dir/venv",
            with_pip=True,
        )
        mock_execv.assert_called_once_with(
            "/mock_proj_dir/venv/bin/python",
            [
                "/mock_proj_dir/venv/bin/python",
                *sys.argv,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_differs_from_path_to_curr_python_and_execv_called(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )

        # when:
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.assert_not_called()
        mock_execv.assert_called_once_with(
            "/opt/bin/python",
            [
                "/opt/bin/python",
                *sys.argv,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()

    @patch(
        f"{proto_code.__name__}.get_path_to_curr_python",
        return_value="/opt/bin/python",
    )
    @patch(f"{proto_code.__name__}.os.execv")
    @patch(f"{proto_code.__name__}.venv.create")
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_path_to_curr_python,
    ):
        # given:
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )
        self.fs.create_file(
            "/mock_proj_dir/conf/python_env.path_to_venv.conf.txt",
            contents="/another/venv\n",
        )
        self.fs.create_dir("/another/venv")

        # when:
        with patch.object(
            self.env_ctx,
            "get_proj_dir",
            return_value="/mock_proj_dir",
        ):
            self.env_ctx.recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.is_not_called()
        mock_execv.assert_called_once_with(
            "/another/venv/bin/python",
            [
                "/another/venv/bin/python",
                *sys.argv,
            ],
        )
        mock_get_path_to_curr_python.assert_called_once()
