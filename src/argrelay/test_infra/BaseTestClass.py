from os import getcwd
from typing import Union
from unittest import TestCase

from argrelay.misc_helper_common import set_argrelay_dir
from argrelay.test_infra import change_to_known_repo_path


class BaseTestClass(TestCase):
    """
    Root test class with defaults for all tests.
    """

    confusing_result_presence_msg = "remove expected result to avoid confusion"

    test_single_line_no: Union[int, None] = None
    """
    Set this `test_single_line_no` to limit test case having `line_no()` with that single line only.

    Setting it to `int` (instead of `None`) anywhere will also fail the test case in `tearDownClass()`.
    """

    @classmethod
    def setUpClass(cls):
        with change_to_known_repo_path("."):
            # Set CWD to the project root = `argrelay_dir` (see FS_29_54_67_86 dir structure):
            set_argrelay_dir(getcwd())
        TestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        TestCase.tearDownClass()
        assert cls.test_single_line_no is None, "see docstring for `test_single_line_no`"

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def tearDown(self):
        super().tearDown()

    def skip_test_when_line_is_not_expected(
        self,
        actual_test_single_line_no: int,
        expected_test_single_line_no: int,
    ):
        """
        Use this function to skip running all tests (fail them)
        except the one specified in `expected_test_single_line_no`.
        """

        self.test_single_line_no = actual_test_single_line_no
        if expected_test_single_line_no is not None:
            if actual_test_single_line_no != expected_test_single_line_no:
                raise AssertionError("skip test as line no does not match")
