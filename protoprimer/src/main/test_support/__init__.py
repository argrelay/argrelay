from enum import Enum
from inspect import currentframe
from unittest import TestCase


class BaseTestClass(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None


def assert_test_module_name_embeds_enum_item_name(
    enum_item: Enum,
):
    """
    Ensure caller test module name contains given prod class name.
    """
    caller_frame = currentframe().f_back
    simple_test_module_name = caller_frame.f_globals["__name__"].split(".")[-1]
    simple_prod_enum_item_name = enum_item.name
    _assert_test_name_embeds_prod_name(
        simple_prod_enum_item_name, simple_test_module_name
    )


def _assert_test_name_embeds_prod_name(
    prod_name: str,
    test_name: str,
):
    """
    This function ensures that names in prod code and test code do not diverge due to refactoring.

    That programmatically establishes relationship between prod code and test code via cross-references.
    This function should not be called directly (with its `str` args) -
    that defeat the purpose as strings easily diverge.
    Instead, an appropriate wrapper function should be called with references (e.g., to classes).
    """
    assert prod_name in test_name
