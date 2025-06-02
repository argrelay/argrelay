import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript.boot_env import (
    Bootstrapper_value_env_conf_dir_path,
    EnvContext,
)


# noinspection PyPep8Naming
class ThisTestClass_ensure_conf_dir(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_conf_dir`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        mock_target_dir = os.path.join(
            mock_proj_dir,
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            value_env_conf_dir_path,
            mock_target_dir,
        )
        self.env_ctx.target_dst_dir_path = None

        # when:
        self.env_ctx.ensure_conf_dir()

        # then:
        # no exception happens

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.env_ctx.target_dst_dir_path = os.path.join(
            mock_proj_dir,
            "target_dir",
        )
        self.fs.create_dir(self.env_ctx.target_dst_dir_path)
        self.fs.create_symlink(
            value_env_conf_dir_path,
            self.env_ctx.target_dst_dir_path,
        )

        # when:
        self.env_ctx.ensure_conf_dir()

        # then:
        # no exception happens

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        actual_target_dir = os.path.join(
            mock_proj_dir,
            "actual_target_dir",
        )
        expected_target_dir = os.path.join(
            mock_proj_dir,
            "expected_target_dir",
        )
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            value_env_conf_dir_path,
            actual_target_dir,
        )
        self.env_ctx.target_dst_dir_path = expected_target_dir

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_conf_dir()

        # then:
        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        mock_not_a_dir = os.path.join(
            mock_proj_dir,
            "file",
        )
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            value_env_conf_dir_path,
            mock_not_a_dir,
        )
        self.env_ctx.target_dst_dir_path = mock_not_a_dir

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_conf_dir()

        # then:
        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.fs.create_dir(value_env_conf_dir_path)

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_conf_dir()

        # then:
        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        self.env_ctx.target_dst_dir_path = os.path.join(
            mock_proj_dir,
            "target_dir",
        )
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.fs.create_dir(mock_proj_dir)
        self.fs.create_dir(self.env_ctx.target_dst_dir_path)

        # when:
        with patch.object(
            self.env_ctx,
            "ensure_allowed_conf_symlink_target",
        ):
            self.env_ctx.ensure_conf_dir()

        # then:
        self.assertTrue(os.path.islink(value_env_conf_dir_path))
        self.assertEqual(
            os.readlink(value_env_conf_dir_path), self.env_ctx.target_dst_dir_path
        )

    @patch(
        f"protoscript.boot_env.{Bootstrapper_value_env_conf_dir_path.__name__}.bootstrap_value"
    )
    def test_failure_when_conf_symlink_is_missing_and_no_target_dir_is_given(
        self,
        mock_value_env_conf_dir_path,
    ):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        self.env_ctx.target_dst_dir_path = None
        value_env_conf_dir_path = os.path.join(
            mock_proj_dir,
            self.env_ctx.default_env_conf_dir_rel_path,
        )
        mock_value_env_conf_dir_path.return_value = value_env_conf_dir_path
        self.fs.create_dir(mock_proj_dir)

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_conf_dir()

        # then:
        self.assertIn("not provided", str(ctx.exception))
