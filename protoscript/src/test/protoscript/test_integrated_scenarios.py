import os
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase

from protoscript import boot_env
from protoscript.boot_env import (
    EnvContext,
    main,
)


class ThisTestClass(PyfakefsTestCase):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          integrated tests for scenarios listed in spec
    """

    def setUp(self):
        self.setUpPyfakefs()

    def test_bootstrap_fails_on_proj_dir_has_no_signature_file(self):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        path_to_signature_file = os.path.join(
            "conf_proj",
            EnvContext.default_proj_config_rel_path,
        )
        self.fs.create_dir(mock_proj_dir)
        test_args = [
            os.path.basename(boot_env.__file__),
            "--proj_conf",
            path_to_signature_file,
        ]

        # when/then:
        with patch.object(sys, "argv", test_args):
            with patch("os.getcwd", return_value=mock_proj_dir):
                with self.assertRaises(AssertionError) as cm:
                    main()
                self.assertIn(
                    "does not contain the required signature file", str(cm.exception)
                )

    def test_bootstrap_succeeds_on_proj_dir_has_signature_file(self):
        # given:
        mock_proj_dir = "/mock_proj_dir"
        path_to_signature_file = os.path.join(
            "conf_proj",
            EnvContext.default_proj_config_rel_path,
        )
        self.fs.create_dir(mock_proj_dir)
        self.fs.create_file(
            os.path.join(
                mock_proj_dir,
                path_to_signature_file,
            ),
            contents="{}",
        )
        test_args = [
            os.path.basename(boot_env.__file__),
            "--proj_conf",
            path_to_signature_file,
        ]

        # when/then:
        with patch.object(sys, "argv", test_args):
            with patch("os.getcwd", return_value=mock_proj_dir):
                with self.assertRaises(AssertionError) as cm:
                    main()
                self.assertNotIn(
                    "does not contain the required signature file", str(cm.exception)
                )
