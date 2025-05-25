from inspect import currentframe

from argrelay_test_infra.test_infra import (
    file_line,
    line_no,
    line_no_from_ctor,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.TestCase import TestCase


class ThisTestCase(TestCase):

    def __init__(self):
        super().__init__(
            line_no_from_ctor(),
            line_no_from_ctor.__name__,
        )


class ThisTestClass(BaseTestClass):

    def test_line_no(self):
        self.assertEqual(
            currentframe().f_lineno + 1,
            line_no(),
        )

    def test_line_no_from_ctor(self):
        self.assertEqual(
            currentframe().f_lineno + 1,
            ThisTestCase().line_no,
        )

    def test_file_line(self):
        self.assertEqual(
            f"{currentframe().f_code.co_filename}:{currentframe().f_lineno + 1}",
            file_line(),
        )
