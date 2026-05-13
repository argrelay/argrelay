import argrelay
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from offline_tests.test_infra.package_version_verifier import verify_package_version


class ThisTestClass(BaseTestClass):

    def test_argrelay_version(self):
        self.assertTrue(verify_package_version(argrelay))
