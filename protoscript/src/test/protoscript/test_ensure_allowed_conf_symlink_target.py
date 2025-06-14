import argparse
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript import proto_code
from protoscript.proto_code import (
    Bootstrapper_state_parsed_args,
    EnvContext,
)


# noinspection PyPep8Naming
class ThisTestClass_ensure_allowed_conf_symlink_target(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_allowed_conf_symlink_target`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_on_valid_relative_dir(
        self,
        mock_state_parsed_args,
    ):
        # given:
        self.fs.create_dir("valid_dir")
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="valid_dir"
        )

        # when:
        self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        # no exception happens

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_on_absolute_path(
        self,
        mock_state_parsed_args,
    ):
        # given:
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="/abs/path"
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must not be absolute", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_on_path_with_dot_dot(
        self,
        mock_state_parsed_args,
    ):
        # given:
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="conf/../bad"
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must not contain `..`", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_on_non_directory_path(
        self,
        mock_state_parsed_args,
    ):
        # given:
        self.fs.create_file("not_a_dir")
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="not_a_dir"
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_on_non_existent_path(
        self,
        mock_state_parsed_args,
    ):
        # given:
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="missing_dir"
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        self.assertIn("must lead to a directory", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_on_symlink_leading_to_a_dir(
        self,
        mock_state_parsed_args,
    ):
        # given:
        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path="symlink_to_dir"
        )

        # when:
        self.env_ctx.ensure_allowed_conf_symlink_target()

        # then:
        # no exception happens
