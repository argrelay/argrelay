import os

from argrelay_test_infra.test_infra.case_condition import (
    skip_test_env,
)


def pytest_collection_modifyitems(config, items):

    # These tests require a real `mongodb` server (instead of `mongomock`):
    skip_test_env(
        os.path.dirname(__file__),
        config,
        items,
    )
