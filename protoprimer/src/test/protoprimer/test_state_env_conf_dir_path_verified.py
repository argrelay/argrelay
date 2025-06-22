import argparse
import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_env_conf_dir_path,
    Bootstrapper_state_parsed_args,
    ConfConstClient,
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
            EnvState.state_env_conf_dir_path_verified
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        mock_target_dir = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            mock_target_dir,
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=None,
        )

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        # no exception happens

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=target_dst_dir_path,
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            target_dst_dir_path,
        )

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        # no exception happens

    @patch(
        f"{proto_code  .__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        actual_target_dir = os.path.join(
            "actual_target_dir",
        )
        expected_target_dir = os.path.join(
            "expected_target_dir",
        )
        state_env_conf_dir_path = os.path.join(
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            actual_target_dir,
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=expected_target_dir,
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_not_a_dir = os.path.join(
            "file",
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_env_conf_dir_path,
            mock_not_a_dir,
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=mock_not_a_dir,
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertIn("target is not a directory", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(state_env_conf_dir_path)
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=None,
        )

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=target_dst_dir_path,
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(target_dst_dir_path)

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertTrue(os.path.islink(state_env_conf_dir_path))
        self.assertEqual(
            os.readlink(state_env_conf_dir_path),
            target_dst_dir_path,
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        target_dst_dir_path_non_normalized = "target_dir/"
        target_dst_dir_path_normalized = "target_dir"
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=target_dst_dir_path_non_normalized,
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path
        self.fs.create_dir(target_dst_dir_path_normalized)

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertTrue(os.path.islink(state_env_conf_dir_path))
        self.assertEqual(
            os.readlink(state_env_conf_dir_path),
            target_dst_dir_path_normalized,
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_env_conf_dir_path.__name__}.bootstrap_state"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_parsed_args.__name__}._bootstrap_once"
    )
    def test_failure_when_conf_symlink_is_missing_and_no_target_dir_is_given(
        self,
        mock_state_parsed_args,
        mock_state_env_conf_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_parsed_args.return_value = argparse.Namespace(
            target_dst_dir_path=None,
        )
        state_env_conf_dir_path = os.path.join(
            mock_client_dir,
            ConfConstClient.default_dir_rel_path_conf_env_link_name,
        )
        mock_state_env_conf_dir_path.return_value = state_env_conf_dir_path

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.bootstrap_state(EnvState.state_env_conf_dir_path_verified)

        # then:
        self.assertIn("not provided", str(ctx.exception))
