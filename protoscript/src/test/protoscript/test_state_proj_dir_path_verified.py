import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript import proto_code
from protoscript.proto_code import (
    Bootstrapper_state_proj_conf_man_file_path,
    Bootstrapper_state_proj_dir_path_configured,
    ConfConstProj,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass_state_proj_dir_path_verified(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          unit tests for `state_proj_dir_path_verified`
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_proj_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_proj_conf_man_file_path.__name__}._bootstrap_once"
    )
    def test_state_proj_conf_man_file_path_exists(
        self,
        mock_state_proj_conf_man_file_path,
        mock_state_proj_dir_path_configured,
    ):

        # given:
        mock_proj_dir = "/mock_proj_dir"
        mock_state_proj_dir_path_configured.return_value = mock_proj_dir
        mock_state_proj_conf_man_file_path.return_value = os.path.join(
            mock_proj_dir,
            ConfConstProj.default_file_basename_conf_proj,
        )
        self.fs.create_file(
            self.env_ctx.bootstrap_state(EnvState.state_proj_conf_man_file_path),
            # TODO: Technically, this content is wrong:
            contents="# test dummy",
        )

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_proj_dir_path_verified)

        # then:
        # no exception happens

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_proj_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_proj_conf_man_file_path.__name__}._bootstrap_once"
    )
    def test_state_proj_conf_man_file_path_missing(
        self,
        mock_state_proj_conf_man_file_path,
        mock_state_proj_dir_path_configured,
    ):

        # given:
        mock_proj_dir = "/mock_proj_dir"
        mock_state_proj_dir_path_configured.return_value = mock_proj_dir
        mock_state_proj_conf_man_file_path.return_value = os.path.join(
            mock_proj_dir,
            ConfConstProj.default_file_basename_conf_proj,
        )
        self.fs.create_dir(mock_proj_dir)

        # when:
        with self.assertRaises(AssertionError) as cm:
            self.env_ctx.bootstrap_state(EnvState.state_proj_dir_path_verified)

        # then:
        self.assertIn("does not contain the required file", str(cm.exception))
