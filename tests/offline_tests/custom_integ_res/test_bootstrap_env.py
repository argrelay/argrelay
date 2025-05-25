import os
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from argrelay.custom_integ_res import bootstrap_env
from argrelay.custom_integ_res.bootstrap_env import (
    ensure_allowed_conf_symlink_target,
    ensure_argrelay_dir,
    ensure_conf_dir,
    ensure_min_python_version,
    get_argrelay_dir,
    main,
    read_line_file,
    recurse_with_required_python_interpreter,
    write_line_file,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass


class ThisTestClass_basic(BaseTestClass):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          basic unit tests
    """

    def test_get_argrelay_dir_returns_curr_dir(self):
        self.assertEqual(
            os.getcwd(),
            get_argrelay_dir(),
        )

    @patch("sys.version_info", (3, 9, 0))
    def test_version_succeeds(self):
        # FS_84_11_73_28: supported python versions:
        ensure_min_python_version()

    @patch("sys.version_info", (3, 7, 5))
    def test_version_fails(self):
        # FS_84_11_73_28: supported python versions:
        with self.assertRaises(AssertionError) as context:
            ensure_min_python_version()
        self.assertIn("below the min required", str(context.exception))


class TestReadWriteLineFile(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `read_line_file` and `write_line_file`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.create_dir("/mock")
        self.test_file = "/mock/test.txt"

    def test_write_line_file_creates_file_with_line(self):
        # given:
        single_line = "/test/line"

        # when:
        write_line_file(self.test_file, single_line)

        # then:
        with open(self.test_file, "r") as f:
            file_contents = f.read()
        self.assertEqual(file_contents, single_line + "\n")

    def test_read_line_file_reads_line_without_newline(self):
        # given:
        self.fs.create_file(self.test_file, contents="/test/line\n")

        # when:
        result = read_line_file(self.test_file)

        # then:
        self.assertEqual(result, "/test/line")

    def test_read_line_file_strips_extra_whitespace(self):
        # given:
        self.fs.create_file(self.test_file, contents="   /test/line   \n")
        # when:
        single_line = read_line_file(self.test_file)
        # then:
        self.assertEqual(single_line, "/test/line")

    def test_write_and_read_consistency(self):
        single_line = "/test/line"
        write_line_file(self.test_file, single_line)
        result = read_line_file(self.test_file)
        self.assertEqual(result, single_line)


# noinspection PyPep8Naming
class ThisTestClass_ensure_argrelay_dir(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_argrelay_dir`
    """

    def setUp(self):
        self.setUpPyfakefs()

    def test_signature_file_exists(self):
        self.fs.create_file(
            "/mock_argrelay_dir/exe/bootstrap_env.py",
            contents="# test dummy",
        )

        with patch(
            "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
            return_value="/mock_argrelay_dir",
        ):
            ensure_argrelay_dir()

    def test_signature_file_missing(self):
        self.fs.create_dir("/mock_argrelay_dir/exe")

        with patch(
            "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
            return_value="/mock_argrelay_dir",
        ):
            with self.assertRaises(AssertionError) as cm:
                ensure_argrelay_dir()
            self.assertIn(
                "does not contain the required signature file", str(cm.exception)
            )


# noinspection PyPep8Naming
class ThisTestClass_ensure_allowed_conf_symlink_target(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_allowed_conf_symlink_target`
    """

    def setUp(self):
        self.setUpPyfakefs()

    def test_success_on_valid_relative_dir(self):
        self.fs.create_dir("valid_dir")
        result = ensure_allowed_conf_symlink_target("valid_dir")
        self.assertTrue(result)

    def test_failure_on_absolute_path(self):
        with self.assertRaises(AssertionError) as ctx:
            ensure_allowed_conf_symlink_target("/abs/path")
        self.assertIn("must not be absolute", str(ctx.exception))

    def test_failure_on_path_with_dot_dot(self):
        with self.assertRaises(AssertionError) as ctx:
            ensure_allowed_conf_symlink_target("conf/../bad")
        self.assertIn("must not contain `..`", str(ctx.exception))

    def test_failure_on_non_directory_path(self):
        self.fs.create_file("not_a_dir")
        with self.assertRaises(AssertionError) as ctx:
            ensure_allowed_conf_symlink_target("not_a_dir")
        self.assertIn("must lead to a directory", str(ctx.exception))

    def test_failure_on_non_existent_path(self):
        with self.assertRaises(AssertionError) as ctx:
            ensure_allowed_conf_symlink_target("missing_dir")
        self.assertIn("must lead to a directory", str(ctx.exception))

    def test_success_on_symlink_leading_to_a_dir(self):
        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        ensure_allowed_conf_symlink_target("symlink_to_dir")


# noinspection PyPep8Naming
class ThisTestClass_ensure_conf_dir(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_conf_dir`
    """

    def setUp(self):
        self.setUpPyfakefs()

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_get_dir,
    ):
        # given:
        self.fs.create_dir("/mock_argrelay_dir/conf_target")
        self.fs.create_symlink(
            "/mock_argrelay_dir/conf", "/mock_argrelay_dir/conf_target"
        )

        # when:
        ensure_conf_dir("/mock_argrelay_dir/conf_target")  # Should pass without error

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_get_dir,
    ):
        # given:
        self.fs.create_dir("/mock_argrelay_dir/actual")
        self.fs.create_dir("/mock_argrelay_dir/expected")
        self.fs.create_symlink("/mock_argrelay_dir/conf", "/mock_argrelay_dir/actual")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            ensure_conf_dir("/mock_argrelay_dir/expected")

        # then:
        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file("/mock_argrelay_dir/file")
        self.fs.create_symlink("/mock_argrelay_dir/conf", "/mock_argrelay_dir/file")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            ensure_conf_dir("/mock_argrelay_dir/file")

        # then:
        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_get_dir,
    ):
        # given:
        self.fs.create_dir("/mock_argrelay_dir/conf")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            ensure_conf_dir("/mock_argrelay_dir/conf")

        # then:
        self.assertIn("is not a symlink", str(ctx.exception))

    @patch("argrelay.custom_integ_res.bootstrap_env.ensure_allowed_conf_symlink_target")
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_get_dir,
        mock_allow_target,
    ):
        # given:
        self.fs.create_dir("/mock_argrelay_dir")
        self.fs.create_dir("/mock_argrelay_dir/target")

        # when:
        ensure_conf_dir("/mock_argrelay_dir/target")

        # then:
        self.assertTrue(os.path.islink("/mock_argrelay_dir/conf"))
        self.assertEqual(
            os.readlink("/mock_argrelay_dir/conf"), "/mock_argrelay_dir/target"
        )

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    def test_failure_when_conf_symlink_is_missing_and_no_target_dir_is_given(
        self,
        mock_get_dir,
    ):
        # given:
        self.fs.create_dir("/mock_argrelay_dir")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            ensure_conf_dir(None)

        # then:
        self.assertIn("not provided", str(ctx.exception))


# noinspection PyPep8Naming
class ThisTestClass_recurse_with_required_python_interpreter(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `recurse_with_required_python_interpreter`
    """

    def setUp(self):
        self.setUpPyfakefs()

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_success_writing_path_to_python_when_missing_and_path_to_curr_python_is_outside_of_path_to_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        path_to_python_path = (
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt"
        )

        # when:
        recurse_with_required_python_interpreter()

        # then:
        path_to_python_value = read_line_file(path_to_python_path)
        self.assertEqual(path_to_python_value, "/usr/bin/python3")
        mock_venv_create.assert_called_once_with(
            "/mock_argrelay_dir/venv",
            with_pip=True,
        )
        mock_execv.assert_called_once_with(
            "/mock_argrelay_dir/venv/bin/python",
            [
                "/mock_argrelay_dir/venv/bin/python",
                *sys.argv,
            ],
        )

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_failure_when_path_to_python_is_inside_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt",
            contents="venv/bin/python\n",
        )

        # when
        with self.assertRaises(AssertionError) as cm:
            recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance.",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/mock_argrelay_dir/venv/bin/python",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_failure_when_path_to_curr_python_is_inside_venv_but_path_to_python_is_still_missing(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )

        # when
        with self.assertRaises(AssertionError) as cm:
            recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"still does not exists",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/mock_argrelay_dir/venv/wrong/path/to/python",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_failure_when_path_to_curr_python_is_inside_venv_but_different_from_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_venv.conf.txt",
            contents="venv\n",
        )
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )

        # when
        with self.assertRaises(AssertionError) as cm:
            recurse_with_required_python_interpreter()

        # then:
        self.assertIn(
            f"it does not match expected interpreter",
            str(cm.exception),
        )

        mock_venv_create.assert_not_called()
        mock_execv.assert_not_called()

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_success_when_path_to_python_matches_interpreter_and_venv_does_not_exist(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt",
            contents="/usr/bin/python3\n",
        )

        # when:
        recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.assert_called_once_with(
            "/mock_argrelay_dir/venv",
            with_pip=True,
        )
        mock_execv.assert_called_once_with(
            "/mock_argrelay_dir/venv/bin/python",
            [
                "/mock_argrelay_dir/venv/bin/python",
                *sys.argv,
            ],
        )

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/usr/bin/python3",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_success_when_path_to_python_differs_from_path_to_curr_python_and_execv_called(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )

        # when:
        recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.assert_not_called()
        mock_execv.assert_called_once_with(
            "/opt/bin/python",
            [
                "/opt/bin/python",
                *sys.argv,
            ],
        )

    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_argrelay_dir",
        return_value="/mock_argrelay_dir",
    )
    @patch(
        "argrelay.custom_integ_res.bootstrap_env.get_path_to_curr_python",
        return_value="/opt/bin/python",
    )
    @patch("argrelay.custom_integ_res.bootstrap_env.os.execv")
    @patch("argrelay.custom_integ_res.bootstrap_env.venv.create")
    def test_success_when_path_to_python_is_not_inside_existing_venv(
        self,
        mock_venv_create,
        mock_execv,
        mock_get_py,
        mock_get_dir,
    ):
        # given:
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_python.conf.txt",
            contents="/opt/bin/python\n",
        )
        self.fs.create_file(
            "/mock_argrelay_dir/conf/python_env.path_to_venv.conf.txt",
            contents="/another/venv\n",
        )
        self.fs.create_dir("/another/venv")

        # when:
        recurse_with_required_python_interpreter()

        # then:
        mock_venv_create.is_not_called()
        mock_execv.assert_called_once_with(
            "/another/venv/bin/python",
            [
                "/another/venv/bin/python",
                *sys.argv,
            ],
        )


class ThisTestClass_integrated_scenarios(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          integrated tests for scenarios listed in spec
    """

    def setUp(self):
        self.setUpPyfakefs()

    def test_bootstrap_fails_on_argrelay_dir_has_no_signature_file(self):
        # given:
        self.fs.create_dir("/argrelay_dir/")
        test_args = [os.path.basename(bootstrap_env.__file__)]

        # when/then:
        with patch.object(sys, "argv", test_args):
            with patch("os.getcwd", return_value="/argrelay_dir/"):
                with self.assertRaises(AssertionError) as cm:
                    main()
                self.assertIn(
                    "does not contain the required signature file", str(cm.exception)
                )

    def test_bootstrap_succeeds_on_argrelay_dir_has_signature_file(self):
        # given:
        self.fs.create_dir("/argrelay_dir/")
        self.fs.create_file(
            "/argrelay_dir/exe/bootstrap_env.py", contents="# test dummy"
        )
        test_args = [os.path.basename(bootstrap_env.__file__)]

        # when/then:
        with patch.object(sys, "argv", test_args):
            with patch("os.getcwd", return_value="/argrelay_dir/"):
                with self.assertRaises(AssertionError) as cm:
                    main()
                self.assertNotIn(
                    "does not contain the required signature file", str(cm.exception)
                )
