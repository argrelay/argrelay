import argparse
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_parsed_args,
    EnvContext,
    EnvState,
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
            EnvState.state_target_dst_dir_path_verified
        )

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
        self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

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
            self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

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
            self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

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
            self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

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
            self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

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
        self.env_ctx.bootstrap_state(EnvState.state_target_dst_dir_path_verified)

        # then:
        # no exception happens
