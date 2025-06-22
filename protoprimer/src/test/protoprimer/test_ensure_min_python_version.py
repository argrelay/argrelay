from unittest.mock import patch

from protoprimer.proto_code import (
    ensure_min_python_version,
)
from test_support import BaseTestClass


class ThisTestClass(BaseTestClass):
    """
    TODO: TODO_11_66_62_70: python_bootstrap:
          basic unit tests
    """

    @patch("sys.version_info", (3, 9, 0))
    def test_version_succeeds(self):
        # FS_84_11_73_28: supported python versions:
        ensure_min_python_version()

    @patch("sys.version_info", (3, 7, 5))
    def test_version_fails(self):
        # FS_84_11_73_28: supported python versions:
        with self.assertRaises(AssertionError) as context:
            ensure_min_python_version()
        self.assertIn("below the min required", str(context.exception))
