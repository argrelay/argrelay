import json
import os
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_client_conf_file_path,
    Bootstrapper_state_client_dir_path_configured,
    ConfConstPrimer,
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
            EnvState.state_client_conf_file_data
        )

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_conf_file_path.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_path_exists(
        self,
        mock_state_client_conf_file_path,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_dir_path_configured.return_value = mock_client_dir
        state_client_conf_file_path = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_path.return_value = state_client_conf_file_path
        self.fs.create_file(
            state_client_conf_file_path,
            contents=json.dumps({}),
        )

        # when:
        self.assertTrue(os.path.isfile(state_client_conf_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data)

        # then:
        # no exception happens

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_client_conf_file_path.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_path_missing(
        self,
        mock_state_client_conf_file_path,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_dir_path_configured.return_value = mock_client_dir
        state_client_conf_file_path = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_path.return_value = state_client_conf_file_path

        # when:
        self.assertFalse(os.path.isfile(state_client_conf_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data)

        # then:
        # file created:
        self.assertTrue(os.path.isfile(state_client_conf_file_path))
