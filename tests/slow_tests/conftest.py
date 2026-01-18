import os

from argrelay_test_infra.test_infra.case_condition import (
    skip_test_integ,
)


def pytest_collection_modifyitems(config, items):

    skip_test_integ(
        os.path.dirname(__file__),
        config,
        items,
    )
