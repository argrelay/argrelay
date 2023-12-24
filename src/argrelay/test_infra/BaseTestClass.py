from os import getcwd
from unittest import TestCase

from argrelay.misc_helper_common import set_argrelay_dir
from argrelay.test_infra import change_to_known_repo_path


class BaseTestClass(TestCase):
    """
    Root test class with defaults for all tests.
    """

    confusing_result_presence_msg = "remove expected result to avoid confusion"

    @classmethod
    def setUpClass(cls):
        with change_to_known_repo_path("."):
            # Set CWD to the project root = `argrelay_dir` (see FS_29_54_67_86 dir structure):
            set_argrelay_dir(getcwd())
        TestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        TestCase.tearDownClass()

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def tearDown(self):
        super().tearDown()
