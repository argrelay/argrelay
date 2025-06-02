import argparse
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript.boot_env import (
    EnvContext,
    EnvValue,
)


# noinspection PyPep8Naming
class ThisTestClass_ensure_proj_dir(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `ensure_proj_dir`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    @patch("protoscript.boot_env.Bootstrapper_value_proj_dir_path._bootstrap_once")
    @patch("protoscript.boot_env.Bootstrapper_value_parsed_args._bootstrap_once")
    def test_signature_file_exists(
        self,
        mock_value_parsed_args,
        mock_value_proj_dir_path,
    ):

        # given:
        mock_proj_dir = "/mock_proj_dir"
        mock_value_parsed_args.return_value = argparse.Namespace(
            proj_conf=EnvContext.default_proj_config_rel_path
        )
        mock_value_proj_dir_path.return_value = mock_proj_dir
        self.fs.create_file(
            self.env_ctx.bootstrap_value(EnvValue.value_proj_conf_man_file_path),
            # TODO: Technically, this content is wrong:
            contents="# test dummy",
        )

        # when:
        self.env_ctx.ensure_proj_dir()

        # then:
        # no exception happens

    @patch("protoscript.boot_env.Bootstrapper_value_proj_dir_path._bootstrap_once")
    @patch("protoscript.boot_env.Bootstrapper_value_parsed_args._bootstrap_once")
    def test_signature_file_missing(
        self,
        mock_value_parsed_args,
        mock_value_proj_dir_path,
    ):

        # given:
        mock_proj_dir = "/mock_proj_dir"
        mock_value_parsed_args.return_value = argparse.Namespace(
            proj_conf=EnvContext.default_proj_config_rel_path
        )
        mock_value_proj_dir_path.return_value = mock_proj_dir
        self.fs.create_dir(mock_proj_dir)

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.ensure_proj_dir()

        # then:
        self.assertIn("does not contain the required signature file", str(cm.exception))
