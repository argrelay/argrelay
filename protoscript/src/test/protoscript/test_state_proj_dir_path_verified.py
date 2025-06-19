import json
import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript import proto_code
from protoscript.proto_code import (
    Bootstrapper_state_proj_conf_man_file_path,
    Bootstrapper_state_proj_dir_path_configured,
    ConfConstPrimer,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(PyfakefsTestCase):

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
        self.fs.create_dir(mock_proj_dir)
        os.chdir(mock_proj_dir)
        mock_state_proj_dir_path_configured.return_value = mock_proj_dir
        state_proj_conf_man_file_path = os.path.join(
            mock_proj_dir,
            ConfConstPrimer.default_file_basename_conf_proj,
        )
        mock_state_proj_conf_man_file_path.return_value = state_proj_conf_man_file_path
        self.fs.create_file(
            state_proj_conf_man_file_path,
            contents=json.dumps({}),
        )

        # when:
        self.assertTrue(os.path.isfile(state_proj_conf_man_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_proj_conf_man_file_data)

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
        self.fs.create_dir(mock_proj_dir)
        os.chdir(mock_proj_dir)
        mock_state_proj_dir_path_configured.return_value = mock_proj_dir
        state_proj_conf_man_file_path = os.path.join(
            mock_proj_dir,
            ConfConstPrimer.default_file_basename_conf_proj,
        )
        mock_state_proj_conf_man_file_path.return_value = state_proj_conf_man_file_path

        # when:
        self.assertFalse(os.path.isfile(state_proj_conf_man_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_proj_conf_man_file_data)

        # then:
        # file created:
        self.assertTrue(os.path.isfile(state_proj_conf_man_file_path))
