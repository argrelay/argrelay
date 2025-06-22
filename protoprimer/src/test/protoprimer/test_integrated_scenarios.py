import os
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoprimer import proto_code
from protoprimer.proto_code import (
    Bootstrapper_state_script_dir_path,
    ArgConst,
    ConfConstPrimer,
    main,
)


class ThisTestClass(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          implement bootstrap scenarios progressively: from nothing (and failing) to the last succeeding one
    """

    def setUp(self):
        self.setUpPyfakefs()

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    def test_bootstrap_proceeds_on_missing_conf_client_file_fails_on_missing_target_dst_dir_path(
        self,
        mock_state_script_dir_path,
    ):
        # given:
        mock_client_dir = "mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mock_state_script_dir_path.return_value = script_dir
        self.fs.create_dir(script_dir)
        test_args = [
            os.path.basename(proto_code.__file__),
            ArgConst.arg_client_dir_path,
            mock_client_dir,
        ]

        # when/then:
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as cm:
                main()
            self.assertIn("`target_dst_dir_path` is not provided", str(cm.exception))

    @patch(
        f"{proto_code.__name__}.{Bootstrapper_state_script_dir_path.__name__}._bootstrap_once"
    )
    def test_bootstrap_proceeds_on_existing_conf_client_file_fails_on_missing_target_dst_dir_path(
        self,
        mock_state_script_dir_path,
    ):
        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mock_state_script_dir_path.return_value = script_dir
        self.fs.create_dir(script_dir)
        test_args = [
            os.path.basename(proto_code.__file__),
            ArgConst.arg_client_dir_path,
            mock_client_dir,
        ]
        self.fs.create_file(
            os.path.join(
                mock_client_dir,
                ConfConstPrimer.default_file_rel_path_conf_client,
            ),
            contents="{}",
        )

        # when/then:
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as cm:
                main()
            self.assertIn("`target_dst_dir_path` is not provided", str(cm.exception))
